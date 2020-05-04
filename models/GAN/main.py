"""
To run this template just do:
python generative_adversarial_net.py

After a few epochs, launch TensorBoard to see the images being generated at every batch:

tensorboard --logdir default
"""
from argparse import ArgumentParser

from models import GAN
from pytorch_lightning.trainer import Trainer


def main(hparams):
    # ------------------------
    # 1 INIT LIGHTNING MODEL
    # ------------------------
    model = GAN(hparams)

    # ------------------------
    # 2 INIT TRAINER
    # ------------------------
    trainer = Trainer(gpus=1)

    # ------------------------
    # 3 START TRAINING
    # ------------------------
    trainer.fit(model)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--dataroot', type=str, default='/data', help='')
    parser.add_argument("--batch_size", type=int, default=64, help="size of the batches")
    parser.add_argument('--image_shape', nargs=3, type=int, default=(3, 64, 64), help='shape of the image')
    parser.add_argument('--gen_coef', type=int, default=64, help='scaling coefficient of generator')
    parser.add_argument('--dis_coef', type=int, default=64, help='scaling coefficient of discriminator')
    parser.add_argument('--num_workers', type=int, default=2, help='number of cpu workers')
    parser.add_argument("--lr", type=float, default=0.0002, help="adam: learning rate")
    parser.add_argument("--b1", type=float, default=0.5,
                        help="adam: decay of first order momentum of gradient")
    parser.add_argument("--b2", type=float, default=0.999,
                        help="adam: decay of first order momentum of gradient")
    parser.add_argument("--latent_dim", type=int, default=100,
                        help="dimensionality of the latent space")

    hparams = parser.parse_args()

    main(hparams)