from pathlib import Path
from flask import Flask, request
import redis
from werkzeug.utils import secure_filename
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.storage import RedisStorage
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN
import torch
import torchvision.transforms as transforms
# dimension = 500
from .utils import align_image, draw_boxes, serve_pil_image

from .discriminator import Discriminator
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

discriminator = Discriminator((3, 64, 64), 64)
discriminator.load_state_dict(torch.load('./discriminator.ckp'))
discriminator = discriminator.eval().to(device)
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize(64),
    transforms.CenterCrop(64),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

dimension = 512

r = redis.Redis(
    host='redis',
    port=6379,
    # charset='utf-8',
    # decode_responses=True,
)
redis_storage = RedisStorage(r)
# Get hash config from redis
config = redis_storage.load_hash_configuration('MyHash')
if config is None:
    # Config is not existing, create hash from scratch, with 10 projections
    lshash = RandomBinaryProjections('MyHash', 50)
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
redis_storage.store_hash_configuration(lshash)

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/identities')
def get_person_list():
    persons = r.smembers('identities')
    app.logger.info(persons)
    return {'identities': [name.decode("utf-8") for name in persons]}


@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    global mtcnn, resnet, engine
    file = request.files['file']
    filename = secure_filename(file.filename)
    current_id = request.form['current_id']
    app.logger.info(current_id)
    im = Image.open(BytesIO(file.read()))
    app.logger.info(f'image size: {im.size}')
    faces, boxes = align_image(im, mtcnn)
    if faces.shape[0] > 1:
        app.logger.warning('multiple faces')
        return 'FUQ'

    face = faces[0]
    box = boxes[0]

    face2disc = transform(face).unsqueeze(dim=0)

    with torch.no_grad():
        score = discriminator(face2disc).item()
    app.logger.info('Discriminator score:', score)
    if score >= 0.8:
        with torch.no_grad():
            embedding = resnet(face.unsqueeze(dim=0)).detach().cpu().numpy()
        boxed_image = draw_boxes(im, [box])

        app.logger.info(embedding)
        engine.store_vector(embedding.reshape(dimension, -1), current_id)
        im_path = Path(data_path, current_id, filename).with_suffix('.jpeg')
        r.sadd(current_id, im_path.name)
        boxed_image.save(im_path)
    else:
        boxed_image = draw_boxes(im, [box], (255, 0, 0))
    return serve_pil_image(boxed_image)


@app.route('/api/add_identity', methods=['POST'])
def add_identity():
    name = request.json['identity']
    if r.sismember('identities', name):
        return 'already in the gallery'
    else:
        r.sadd('identities', name)
        Path(data_path, name).mkdir(exist_ok=True)
        return 'OK'

@app.route('/api/delete_identity', methods=['POST'])
def delete_identity():
    name = request.json['identity']
    if r.sismember('identities', name):
        with r.pipeline() as pipe:
            r.srem('identities', name)
            r.delete(name)
            pipe.execute()
    path = Path(data_path, name)
    shutil.rmtree(path)
    return 'ok'

@app.route('/api/images/<identity>')
def images(identity):
    files = [file.decode("utf-8") for file in r.smembers(identity)]
    return {'files': files}

@app.route('/api/get_image/<identity>/<file>')
def get_image(identity, file):
    return send_file(Path(data_path, identity, file).with_suffix('.jpeg'), mimetype='image/jpeg')

@app.route('/api/detect_face', methods=['POST'])
def detect_face():
    file = request.files['file']
    im = Image.open(BytesIO(file.read()))
    app.logger.info(f'image size: {im.size}')
    faces, boxes = align_image(im, mtcnn)
    if faces.shape[0] > 1:
        app.logger.warning('multiple faces')
        return 'FUQ'

    face = faces[0]
    box = boxes[0]

    if face is None:
        return 0
    face2disc = transform(face).unsqueeze(dim=0)

    with torch.no_grad():
        score = discriminator(face2disc).item()
    app.logger.info('Discriminator score:', score)
    if score >= 0.8:
        with torch.no_grad():
            embedding = resnet(face.unsqueeze(dim=0)).detach().cpu().numpy()
        boxed_image = draw_boxes(im, [box])
        N = engine.neighbours(embedding.reshape(dimension, -1))
        app.logger.info(N)
        if len(N) > 0:
            cls = N[0][1]
            dist = N[0][2]
        else:
            cls = dist = 'Unknown'
    else:
        boxed_image = draw_boxes(im, [box], (255, 0, 0))
        cls = 'Out of sample'
    response = serve_pil_image(boxed_image)
    response.headers.add('X-Extra-Info-JSON',  cls)
    app.logger.info(response.headers.get('X-Extra-Info-JSON'))
    return response
