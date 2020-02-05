#AUTOGENERATED! DO NOT EDIT! File to edit: dev/21_models.modules.ipynb (unless otherwise specified).

__all__ = ['bn_drop_lin', 'ConvBnRelu', 'ConvBn', 'ConvRelu', 'icnr', 'PixelShuffleICNR', 'DecoderBlock', 'LastCross',
           'DynamicUnet', 'CBR', 'TransformerBlock']

#Cell
from .utils import get_sizes
from .hooks import Hooks
from ..imports import *
from torch.nn.functional import interpolate, pad

#Cell
def bn_drop_lin(n_in, n_out, bn=True, p=0., actn=None):
    "Sequence of batchnorm (if `bn`), dropout (with `p`) and linear (`n_in`,`n_out`) layers followed by `actn`."
    layers = [nn.BatchNorm1d(n_in)] if bn else []
    if p != 0: layers.append(nn.Dropout(p))
    layers.append(nn.Linear(n_in, n_out))
    if actn is not None: layers.append(actn)
    return layers

#Cell
class ConvBnRelu(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, bias=True, eps=1e-5, momentum=0.01, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride=stride,
            padding=padding, bias=bias, **kwargs)
        self.bn = nn.BatchNorm2d(
            out_channels, eps=eps, momentum=momentum)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x

class ConvBn(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, bias=True, eps=1e-5, momentum=0.01, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride=stride,
            padding=padding, bias=bias, **kwargs)
        self.bn = nn.BatchNorm2d(
            out_channels, eps=eps, momentum=momentum)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return x

class ConvRelu(nn.Module):
    def __init__(
            self, in_channels, out_channels, kernel_size, stride=1, padding=0,
            bias=True, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride=stride,
            padding=padding, bias=bias, **kwargs)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        return x

#Cell
def icnr(x, scale=2, init=nn.init.kaiming_normal_):
    ni, nf, h, w = x.shape
    ni2 = int(ni/(scale**2))
    k = init(torch.zeros([ni2, nf, h, w])).transpose(0, 1)
    k = k.contiguous().view(ni2, nf, -1)
    k = k.repeat(1, 1, scale**2)
    k = k.contiguous().view([nf, ni, h, w]).transpose(0, 1)
    x.data.copy_(k)

class PixelShuffleICNR(nn.Module):
    def __init__(
            self, in_channels, out_channels, bias=True, scale_factor=2, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels*scale_factor**2, 1, bias=bias, **kwargs)
        icnr(self.conv.weight)
        self.shuf = nn.PixelShuffle(scale_factor)
        # self.pad = nn.ReflectionPad2d((1, 0, 1, 0))
        # self.blur = nn.AvgPool2d(2, stride=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        x = self.shuf(x)
        # x = self.pad(x)
        # x = self.blur(x)
        return x

#Cell
class DecoderBlock(nn.Module):
    def __init__(self, in_chans, skip_chans, hook, final_div=True, **kwargs):
        super().__init__()
        self.hook = hook
        self.shuf = PixelShuffleICNR(in_chans, in_chans//2, **kwargs)
        self.bn = nn.BatchNorm2d(skip_chans)
        ni = in_chans//2 + skip_chans
        nf = ni if not final_div else skip_chans
        self.relu = nn.ReLU()
        self.conv1 = ConvBnRelu(ni, nf, 3, padding=1, **kwargs)
        self.conv2 = ConvBnRelu(nf, nf, 3, padding=1, **kwargs)

    def forward(self, x):
        skipco = self.hook.stored
        x = self.shuf(x)
        ssh = skipco.shape[-2:]
        if ssh != x.shape[-2:]:
            x = interpolate(x, ssh, mode='nearest')
        x = self.relu(torch.cat([x, self.bn(skipco)], dim=1))
        return self.conv2(self.conv1(x))

class LastCross(nn.Module):
    def __init__(self, n_chans, bottle=False):
        super(LastCross, self).__init__()
        n_mid = n_chans//2 if bottle else n_chans
        self.conv1 = ConvBnRelu(n_chans, n_mid, 3, padding=1)
        self.conv2 = ConvBnRelu(n_mid, n_chans, 3, padding=1)

    def forward(self, x):
        y = self.conv1(x)
        y = self.conv2(y)
        return x+y

#Cell
class DynamicUnet(nn.Module):
    def __init__(self, encoder_name, cut=-2, n_classes=2, input_shape=(3, 224, 224), pretrained=True):
        super().__init__()
        encoder = timm.create_model(encoder_name, pretrained=pretrained)
        # encoder = resnet34()
        self.encoder = nn.Sequential(*(list(encoder.children())[:cut]+[nn.ReLU()]))
        encoder_sizes, idxs = self.register_output_hooks(input_shape=input_shape)
        n_chans = encoder_sizes[-1][1]
        middle_conv = nn.Sequential(ConvBnRelu(n_chans, n_chans//2, 3),
                                    ConvBnRelu(n_chans//2, n_chans, 3))
        decoder = [middle_conv]
        for k, (idx, hook) in enumerate(zip(idxs[::-1], self.hooks)):
            skip_chans = encoder_sizes[idx][1]
            final_div = (k != len(idxs)-1)
            decoder.append(DecoderBlock(n_chans, skip_chans, hook, final_div=final_div))
            n_chans = n_chans//2 + skip_chans
            n_chans = n_chans if not final_div else skip_chans
        self.decoder = nn.Sequential(*decoder, PixelShuffleICNR(n_chans, n_chans))
        n_chans += input_shape[0]
        self.head = nn.Sequential(LastCross(n_chans), nn.Conv2d(n_chans, n_classes, 1))


    def forward(self, x):
        y = self.encoder(x)
        y = self.decoder(y)
        if y.shape[-2:] != x.shape[-2:]:
            y = interpolate(y, x.shape[-2:], mode='nearest')
        y = torch.cat([x, y], dim=1)
        y = self.head(y)
        return y


    def register_output_hooks(self, input_shape=(3, 224, 224)):
        sizes, modules = get_sizes(self.encoder, input_shape=input_shape)
        mods = []
        idxs = np.where(sizes[:-1, -1] != sizes[1:, -1])[0]
        def _hook(model, input, output):
            return output

        for k in idxs[::-1]:
            out_shape = sizes[k]
            m = modules[k]
            if 'downsample' not in m.name:
                mods.append(m)
        self.hooks = Hooks(mods, _hook)

        return sizes, idxs

    def __del__(self):
        if hasattr(self, "hooks"): self.hooks.remove()

#Cell
class CBR(nn.Module):
    def __init__(self, kernel_size, n_kernels, n_layers, n_classes=2):
        super().__init__()
        in_c = 3
        out_c = n_kernels
        for k in range(n_layers):
            self.add_module(f'cbr{k}', ConvBnRelu(in_c, out_c, kernel_size, stride=2, padding=kernel_size//2, padding_mode='reflect'))
            # self.add_module(f'maxpool{k}', nn.MaxPool2d(3, stride=2, padding=1))
            in_c = out_c
            out_c *= 2
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.flat = nn.Flatten(-2, -1)
        self.fc = nn.Linear(out_c, n_classes)

    def forward(self, x):
        for m in self.children():
            x = m(x)
        return x

#Cell
class TransformerBlock(nn.Module):
    def __init__(self, c_in, c_out, k, stride=1, groups=1, bias=False):
        super().__init__()
        assert c_in % groups == c_out % groups == 0, "c_in and c_out must be divided by groups"

        padding = k // 2
        self.c_in = c_in
        self.c_out = c_out
        self.k = k
        self.stride = stride
        self.groups = groups

        self.key_conv = nn.Conv2d(c_in, c_out, 1, padding=padding, groups=groups, bias=bias, padding_mode='reflect')
        self.query_conv = nn.Conv2d(c_in, c_out, 1, groups=groups, bias=bias)
        self.value_conv = nn.Conv2d(c_in, c_out, 1, padding=padding, groups=groups, bias=bias, padding_mode='reflect')

    def forward(self, x):
        b, c, h, w = x.shape
        n = self.c_out // self.groups

        q = self.query_conv(x).view(b, self.groups, n, h, w, 1)
        k = self.key_conv(x).unfold(2, self.k, self.stride).unfold(3, self.k, self.stride).view(b, self.groups, n, h, w, -1)
        v = self.value_conv(x).unfold(2, self.k, self.stride).unfold(3, self.k, self.stride).view(b, self.groups, n, h, w, -1)

        # TODO: distance embeddings

        y = (torch.softmax(q*k, dim=-1) * v).sum(-1).view(b, c_out, h, w)

        return y
