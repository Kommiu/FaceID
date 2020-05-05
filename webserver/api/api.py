from pathlib import Path
from flask import Flask, request
import redis
from werkzeug.utils import secure_filename
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.storage import RedisStorage
from PIL import Image
from io import BytesIO
from facenet_pytorch import InceptionResnetV1, MTCNN
import torch
# dimension = 500
from .utils import align_image, draw_boxes, populate_redis
from flask import send_file, jsonify
from io import BytesIO
import shutil

data_path = Path('/home/kommiu/app/data')

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device, keep_all=True,
)
resnet = InceptionResnetV1(pretrained='casia-webface').eval().to(device)

dimension = 512

r = redis.StrictRedis(
    host='redis',
    port=6379,
    charset='utf-8',
    decode_responses=True,
)
populate_redis(r, data_path)
redis_storage = RedisStorage(r)
r.sadd('identities', 'Matt')
r.sadd('identities', 'Anna')

# Get hash config from redis
config = redis_storage.load_hash_configuration('MyHash')
if config is None:
    # Config is not existing, create hash from scratch, with 10 projections
    lshash = RandomBinaryProjections('MyHash', 10)
else:
    # Config is existing, create hash with None parameters
    lshash = RandomBinaryProjections(None, None)
    # Apply configuration loaded from redis
    lshash.apply_config(config)

# Create engine for feature space of 100 dimensions and use our hash.
# This will set the dimension of the lshash only the first time, not when
# using the configuration loaded from redis. Use redis storage to store
# buckets.
engine = Engine(dimension, lshashes=[lshash], storage=redis_storage)

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/identities')
def get_person_list():
    persons = r.smembers('identities')
    app.logger.info(persons)
    return {'identities': list(persons)}


@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    global mtcnn, resnet, engine
    file = request.files['file']
    filename = secure_filename(file.filename)

    app.logger.info('got image')
    im = Image.open(BytesIO(file.read()))
    app.logger.info(f'image size: {im.size}')
    faces, boxes = align_image(im, mtcnn)
    if faces.shape[0] > 1:
        app.logger.warning('multiple faces')
        return 'FUQ'

    face = faces[0]
    box = boxes[0]
    app.logger.info(face.shape)
    with torch.no_grad():
        embedding = resnet(face.unsqueeze(dim=0)).detach().cpu().numpy()

    boxed_image = draw_boxes(im, [box])

    engine.store_vector(embedding.reshape(dimension, -1), 1)
    im_path = Path(data_path, filename)
    boxed_image.save(im_path, 'JPEG')
    return serve_pil_image(boxed_image)


@app.route('/api/add_identity', methods=['POST'])
def add_identity():
    name = request.json['identity']
    app.logger.info(name)
    if r.sismember('identities', name):
        return 'already in the gallery'
    else:
        r.sadd('identities', name)
        Path(data_path, name).mkdir(exist_ok=True)
        return 'OK'

@app.route('/api/delete_identity', methods=['POST'])
def delete_identity():
    name = request.json['identity']
    app.logger.info(f'{name} identity')
    if r.sismember('identities', name):
        with r.pipeline() as pipe:
            r.srem('identities', name)
            r.delete(name)
            pipe.execute()
    path = Path(data_path, name)
    shutil.rmtree(path)
    return 'ok'