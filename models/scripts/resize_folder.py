import argparse
from pathlib import Path
import cv2
from PIL import Image
import numpy as np
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from albumentations import SmallestMaxSize, CenterCrop, Compose
def get_minimal_size(path):
    res = set()
    path = Path(path)
    for p in path.rglob('*'):
        if not p.is_dir():
            im = Image.open(p)
            w, h = im.size
            res.add(w)
            res.add(h)

    return min(res)

class ImageFolderWithPath(ImageFolder):
    def __init__(self, transform, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.albu_transform = transform

    def __getitem__(self, idx):
        img, cls = super().__getitem__(idx)
        path = '/'.join(self.imgs[idx][0].rsplit('/', 2)[1:])
        img = self.albu_transform(image=np.array(img))['image']
        img = Image.fromarray(img)
        return (img, path)


def collate_fn(x):
    return list(zip(*x))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--path_in', type=str, required=True)
    ap.add_argument('-o', '--path_out', type=str, required=True)
    ap.add_argument('-b', '--batch_size', type=int, default=128)
    ap.add_argument('-w', '--num_workers', type=int, default=4)
    args = vars(ap.parse_args())
    size = max(get_minimal_size(args['path_in']), 160)

    transform = Compose([
        SmallestMaxSize(size),
        CenterCrop(size, size),
    ])

    dataset = ImageFolderWithPath(transform, args['path_in'])
    p = Path(args['path_out'])
    for cls in dataset.class_to_idx.keys():
        Path(p, cls).mkdir(parents=True, exist_ok=True)

    dataloader = DataLoader(dataset, collate_fn=collate_fn, batch_size=args['batch_size'], num_workers=args['num_workers'])
    for imgs, paths in dataloader:
        paths = [Path(p, path) for path in paths]
        for i, img, in enumerate(imgs):
            img.save(paths[i].as_posix())








