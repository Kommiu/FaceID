from pathlib import Path
from flask import Flask, request
import redis
from werkzeug.utils import secure_filename
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.storage import RedisStorage
from PIL import Image
from io import BytesIO

# dimension = 500

data_path = Path('/data')

r = redis.StrictRedis(
    host='redis',
    port=6379,
    charset='utf-8',
    decode_responses=True,
)

# redis_storage = RedisStorage(r)
r.sadd('persons', 'Matt')
#
# # Get hash config from redis
# config = redis_storage.load_hash_configuration('MyHash')
# if config is None:
#     # Config is not existing, create hash from scratch, with 10 projections
#     lshash = RandomBinaryProjections('MyHash', 10)
# else:
#     # Config is existing, create hash with None parameters
#     lshash = RandomBinaryProjections(None, None)
#     # Apply configuration loaded from redis
#     lshash.apply_config(config)
#
# # Create engine for feature space of 100 dimensions and use our hash.
# # This will set the dimension of the lshash only the first time, not when
# # using the configuration loaded from redis. Use redis storage to store
# # buckets.
# engine = Engine(100, lshashes=[lshash], storage=redis_storage)


app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/identities')
def get_person_list():
    persons = ['Anna', 'Vanya']#r.smembers('persons')
    return {'identities': list(persons)}


@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file']
    filename = secure_filename(file.filename)

    im = Image.open(BytesIO(file.read()))
    im.save(Path(data_path, filename), 'JPEG')
    return 'FUQ'


# @app.route('/add_person')
# def add_person(name):
#     if r.sismember('persons', name):
#         return False
#     else:
#         r.sadd('persons', name)
#         r.hset(name, 'image', None)
#
# @app.route('/add_image')
# def add_image():
#     name = request.args['name']
#     file = request.files['file']
#     filename = secure_filename(file.filename)
#     if r.sismember('persons', name):
#         pass

