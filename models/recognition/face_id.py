import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

from facenet_pytorch import InceptionResnetV1
from GAN.models import Discriminator

resnet = InceptionResnetV1(pretrained='cassia_webface')

gallery = pd.read_csv('path/to/gallery')

disc = Discriminator()
knn_clf = KNeighborsClassifier(weights='distance', metric='cosine')
knn_clf.fit(gallery.drop('names', axis=1), gallery['names'])


def get_prediction(image_bytes):
    tensor = prepare_image(image_bytes=image_bytes)
    embedding = resnet(tensor).detach().cpu().numpy()
    name = knn_clf.predict(embedding)
    score = disc(tensor).item()

    return name, score
