import logging


import argparse
from pathlib import Path

import redis
import torch
from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
from nearpy.storage import RedisStorage
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from tqdm import tqdm

from api.utils import align_image, draw_boxes
if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--in_path', type=str, required=True)
    ap.add_argument('-o', '--out_path', type=str, required=True)
    ap.add_argument('-b', '--batch_size', type=int, default=128)
    ap.add_argument('-w', '--num_workers', type=int, default=4)
    args = vars(ap.parse_args())


    logging.info('Connecting to Redis')
    r = redis.StrictRedis(
        host='redis',
        port=6379,
        charset='utf-8',
        decode_responses=True,
    )
    redis_storage = RedisStorage(r)

    logging.info('Configuring NearPy')
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
    dimension = 512
    engine = Engine(dimension, lshashes=[lshash], storage=redis_storage)

    # Models:
    logging.info('Loading models')
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device
    )
    resnet = InceptionResnetV1(pretrained='casia-webface').eval().to(device)

    ds = ImageFolder(
        root=args['in_path'],
    )

    def collate_fn(x):
        return list(zip(*x))

    ds.idx_to_class = {i: c for c, i in ds.class_to_idx.items()}
    dl = DataLoader(
        ds,
        batch_size=args['batch_size'],
        shuffle=False,
        num_workers=args['num_workers'],
        collate_fn=collate_fn,
    )


    for imgs, classes in tqdm(dl):
        faces, boxes = align_image(imgs, mtcnn)
        for i, (img, cls, face, box) in enumerate(zip(imgs, classes, faces, boxes)):
            if face is None:
                continue
            boxed_img = draw_boxes(img, [box])
            name = ds.idx_to_class[cls]
            im_path = Path(args['out_path'], name, str(i)).with_suffix('.jpeg')
            im_path.parent.mkdir(exist_ok=True, parents=True)
            boxed_img.save(im_path)
            with torch.no_grad():
                emb = resnet(face.unsqueeze(dim=0)).detach().cpu().squeeze().numpy()
            engine.store_vector(emb.reshape(dimension, -1), name)
            r.sadd(name, im_path.name)
            r.sadd('identities', name)