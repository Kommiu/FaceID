import argparse
from pathlib import Path
from PIL import Image


def get_minimum_resolution(path):
    res = set()
    path = Path(path)
    for p in path.rglob('*'):
        if not p.is_dir():
            im = Image.open(p)
            w, h = im.size
            res.add((w, h))

    return min(res, key=lambda x: x[0]*x[1])
