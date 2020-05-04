import argparse
import torch
from facenet_pytorch import MTCNN

from pathlib import Path
from tqdm import tqdm
import torch
from torch.utils.data import DataLoader
import torchvision.datasets as dset


class ImageFolderWithPath(dset.ImageFolder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, idx):
        img, cls = super().__getitem__(idx)
        path = '/'.join(self.imgs[idx][0].rsplit('/', 2)[1:])
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
        paths = [Path(p, path) for path in paths]
        mtcnn(imgs, save_path=paths)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--path_in', type=str, required=True,
                    help="ip address of the device")
    ap.add_argument('-o', '--path_out', type=str, required=True)
    ap.add_argument('-b', '--batch_size', type=int, default=128)
    ap.add_argument('-w', '--num_workers', type=int, default=4)
    args = vars(ap.parse_args())

    device = device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print('Running on device: {}'.format(device))

    mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=False,
        device=device
    )
    align_folder(mtcnn, args['path_in'], args['path_out'], args['num_workers'], args['batch_size'])
