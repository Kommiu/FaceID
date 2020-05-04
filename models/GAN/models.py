from collections import OrderedDict
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torchvision.datasets as dset
from pytorch_lightning.core import LightningModule


class Generator(nn.Module):
    def __init__(self, latent_dim, image_shape, coef):
        super(Generator, self).__init__()
        self.main = nn.Sequential(
            # input is Z, going into a convolution
            nn.ConvTranspose2d(latent_dim, coef * 8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(coef * 8),
            nn.ReLU(True),
            # state size. (ngf*8) x 4 x 4
            nn.ConvTranspose2d(coef * 8, coef * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(coef * 4),
            nn.ReLU(True),
            # state size. (ngf*4) x 8 x 8
            nn.ConvTranspose2d(coef * 4, coef * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(coef * 2),
            nn.ReLU(True),
            # state size. (ngf*2) x 16 x 16
            nn.ConvTranspose2d(coef * 2, coef, 4, 2, 1, bias=False),
            nn.BatchNorm2d(coef),
            nn.ReLU(True),
            # state size. (ngf) x 32 x 32
            nn.ConvTranspose2d(coef, image_shape[0], 4, 2, 1, bias=False),
            nn.Tanh()
            # state size. (nc) x 64 x 64
        )

    def forward(self, input):
        return self.main(input)


class Discriminator(nn.Module):
    def __init__(self, image_shape, coef):
        super(Discriminator, self).__init__()
        self.main = nn.Sequential(
            # input is (nc) x 64 x 64
            nn.Conv2d(image_shape[0], coef, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf) x 32 x 32
            nn.Conv2d(coef, coef * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(coef * 2),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*2) x 16 x 16
            nn.Conv2d(coef * 2, coef * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(coef * 4),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*4) x 8 x 8
            nn.Conv2d(coef * 4, coef * 8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(coef * 8),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*8) x 4 x 4
            nn.Conv2d(coef * 8, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )

    def forward(self, input):
        return self.main(input)


class GAN(LightningModule):

    def __init__(self, hparams):
        super().__init__()
        self.hparams = hparams

        # networks
        self.generator = Generator(
            latent_dim=hparams.latent_dim,
            image_shape=hparams.image_shape,
            coef=hparams.gen_coef,
        )
        self.generator.apply(weights_init)
        self.discriminator = Discriminator(
            image_shape=hparams.image_shape,
            coef=hparams.dis_coef,
        )
        self.discriminator.apply(weights_init)

        # cache for generated images
        self.generated_imgs = None
        self.last_imgs = None

    def forward(self, z):
        return self.generator(z)

    def adversarial_loss(self, y_hat, y):
        return F.binary_cross_entropy(y_hat, y)

    def training_step(self, batch, batch_idx, optimizer_idx):
        imgs, _ = batch
        self.last_imgs = imgs

        # train generator
        if optimizer_idx == 0:
            # sample noise
            z = torch.randn(imgs.shape[0], self.hparams.latent_dim, 1, 1)
            z = z.type_as(imgs)

            # generate images
            self.generated_imgs = self(z)

            # log sampled images
            # sample_imgs = self.generated_imgs[:5]
            # grid = torchvision.utils.make_grid(sample_imgs)
            # self.logger.experiment.add_image('generated_images', grid, -1)

            # ground truth result (ie: all fake)
            # put on GPU because we created this tensor inside training_loop
            valid = torch.ones(imgs.size(0), 1)
            valid = valid.type_as(imgs)

            # adversarial loss is binary cross-entropy
            g_loss = self.adversarial_loss(self.discriminator(self.generated_imgs), valid)
            tqdm_dict = {'g_loss': g_loss}
            output = OrderedDict({
                'loss': g_loss,
                'progress_bar': tqdm_dict,
                'log': tqdm_dict
            })
            return output

        # train discriminator
        if optimizer_idx == 1:
            # Measure discriminator's ability to classify real from generated samples

            # how well can it label as real?
            valid = torch.ones(imgs.size(0), 1)
            valid = valid.type_as(imgs)

            real_loss = self.adversarial_loss(self.discriminator(imgs), valid)

            # how well can it label as fake?
            fake = torch.zeros(imgs.size(0), 1)
            fake = fake.type_as(valid)

            fake_loss = self.adversarial_loss(
                self.discriminator(self.generated_imgs.detach()),
                fake
            )

            # discriminator loss is the average of these
            d_loss = (real_loss + fake_loss) / 1
            tqdm_dict = {'d_loss': d_loss}
            output = OrderedDict({
                'loss': d_loss,
                'progress_bar': tqdm_dict,
                'log': tqdm_dict
            })
            return output

    def configure_optimizers(self):
        lr = self.hparams.lr
        b0 = self.hparams.b1
        b1 = self.hparams.b2

        opt_g = torch.optim.Adam(self.generator.parameters(), lr=lr, betas=(b0, b1))
        opt_d = torch.optim.Adam(self.discriminator.parameters(), lr=lr, betas=(b0, b1))
        return [opt_g, opt_d], []

    def train_dataloader(self):
        dataset = dset.ImageFolder(
            root=self.hparams.dataroot,
            transform=transforms.Compose([
                transforms.Resize(self.hparams.image_shape[1:]),
                transforms.CenterCrop(self.hparams.image_shape[1:]),
                transforms.ToTensor(),
                transforms.Normalize((-1.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ])
        )
        dataloader = DataLoader(
            dataset,
            batch_size=self.hparams.batch_size,
            shuffle=True,
            num_workers=self.hparams.num_workers,
        )
        return dataloader

    def on_epoch_end(self):
        z = torch.randn(7, self.hparams.latent_dim)
        z = z.type_as(self.last_imgs)

        # log sampled images
        sample_imgs = self(z)
        grid = torchvision.utils.make_grid(sample_imgs)
        self.logger.experiment.add_image(f'generated_images', grid, self.current_epoch)

def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)