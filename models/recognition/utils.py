from pathlib import Path
from tqdm import tqdm
import torch
from torch.utils.data import DataLoader
from torch.utils.data import dataset as dset


class ImageFolderWithPath(dset.ImageFolder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, idx):
        img, cls = super().__getitem__(idx)
        path = self.imgs[idx][0].split('/', 1)[-1]
        return (img, path)


def align_folder(mtcnn, path_in, path_out, num_workers=4, batch_size=128):
    def collate_fn(x):
        return list(zip(*x))

    dataset = ImageFolderWithPath(path_in)
    loader = DataLoader(dataset, collate_fn=collate_fn, num_workers=num_workers, batch_size=batch_size)
    p = Path(path_out)
    for cls in dataset.class_to_idx.keys():
        Path(p, cls).mkdir(parents=True, exist_ok=True)

    for imgs, paths in tqdm(loader):
        paths = [f'casia-aligned/{path}' for path in paths]
        mtcnn(imgs, save_path=paths)
from pathlib import Path
from PIL import Image


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