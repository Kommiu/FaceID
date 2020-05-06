import torch
import torch.nn as nn

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
        return self.main(input).squeeze()