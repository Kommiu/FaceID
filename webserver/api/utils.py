import torch
from facenet_pytorch.models.mtcnn import fixed_image_standardization
from facenet_pytorch.models.utils.detect_face import extract_face
import numpy as np

from PIL import Image, ImageDraw

def draw_boxes(image, boxes):
    im_draw = image.copy()
    draw = ImageDraw.Draw(im_draw)
    for box in boxes:
        draw.rectangle(box.tolist(), outline=(255, 0, 0), width=6)
    return im_draw


def align_image(image, mtcnn):
    with torch.no_grad():
        batch_boxes, _ = mtcnn.detect(image)
    batch_mode = True
    if not isinstance(image, (list, tuple)) and not (isinstance(image, np.ndarray) and len(image.shape) == 4):
        image = [image]
        batch_boxes = [batch_boxes]
        batch_mode = False

    faces, boxes = [], []
    for im, box_im in zip(image, batch_boxes):
        if box_im is None:
            faces.append(None)
            boxes.append([None] if mtcnn.keep_all else None)
            continue

        if not mtcnn.keep_all:
            box_im = box_im[[0]]

        faces_im = []
        boxes_im = []
        for i, box in enumerate(box_im):
            face = extract_face(im, box, mtcnn.image_size, mtcnn.margin)
            if mtcnn.post_process:
                face = fixed_image_standardization(face)
            faces_im.append(face)
            boxes_im.append(box)

        if mtcnn.keep_all:
            faces_im = torch.stack(faces_im)
        else:
            faces_im = faces_im[0]
            boxes_im = boxes_im[0]

        faces.append(faces_im)
        boxes.append(boxes_im)

    if not batch_mode:
        faces = faces[0]
        boxes = boxes[0]

    return faces, boxes

