
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
import numpy as np
import pandas as pd
import os
import argparse

workers = 3



device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))


mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)

resnet = InceptionResnetV1(pretrained='cassia-webface').eval().to(device)

def collate_fn(x):
    return x[0]

if __name__ == '__main__':

        ap = argparse.ArgumentParser()
        ap.add_argument('-g', '--gallery', type=str, required=True, help='path to image gallery')
        ap.add_argument('-o', 'output_file', type=str, required=True, help='path to output file')
        ap.add_argument('-w', '--workers', type=int, help='number of workers')
        args = vars(ap.parse_args())
        dataset = datasets.ImageFolder(args['gallery'])
        dataset.idx_to_class = {i: c for c, i in dataset.class_to_idx.items()}
        loader = DataLoader(dataset, collate_fn=collate_fn, num_workers=args['workers'])

        aligned = []
        names = []
        for x, y in loader:
            x_aligned, prob = mtcnn(x, return_prob=True)
            if x_aligned is not None:
                print('Face detected with probability: {:8f}'.format(prob))
                aligned.append(x_aligned)
                names.append(dataset.idx_to_class[y])

        aligned = torch.stack(aligned).to(device)
        embeddings = resnet(aligned).detach().cpu().numpy()

        output = pd.DataFrame(embeddings)
        output['names'] = names
        output.to_csv(args['output_file'], index=False)

