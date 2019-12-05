#AUTOGENERATED! DO NOT EDIT! File to edit: dev/08_models_unet.ipynb (unless otherwise specified).

__all__ = ['ConvBnRelu', 'ConvBn', 'ConvRelu', 'icnr', 'PixelShuffleICNR', 'DecoderBlock', 'DynamicUnet']

#Cell
import torch.nn as nn
import timm

#Cell
class ConvBnRelu(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, bias=True, eps=1e-5, momentum=0.01, **kwargs):
        super(ConvBnRelu, self).__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride=stride,
            padding=padding, bias=bias, **kwargs)
        self.bn = nn.BatchNorm2d(
            out_channels, eps=eps, momentum=momentum, **kwargs)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x

class ConvBn(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1,
                 padding=0, bias=True, eps=1e-5, momentum=0.01, **kwargs):
        super(ConvBn, self).__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size, stride=stride,
            padding=padding, bias=bias, **kwargs)
        self.bn = nn.BatchNorm2d(
            out_channels, eps=eps, momentum=momentum, **kwargs)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return x

class ConvRelu(nn.Module):
    def __init__(
            self, in_channels, out_channels, kernel_size, stride=1, padding=0,
            bias=True, **kwargs):
        super(ConvRelu, self).__init__()
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
        super(PixelShuffleICNR, self).__init__()
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
    def __init__(self, in_chans, skip_chans, skip_cos, final_div=True, **kwargs):
        super(DecoderBlock, self).__init__()
        self.skip_cos = skip_cos
        self.shuf = PixelShuffleICNR(in_chans, in_chans//2, **kwargs)
        self.bn = nn.BatchNorm2d(skip_chans)
        ni = in_chans//2 + skip_chans
        nf = ni if not final_div else skip_chans
        self.relu = nn.ReLU()
        self.conv1 = ConvBnRelu(ni, nf, 3, padding=1, **kwargs)
        self.conv2 = ConvBnRelu(nf, nf, 3, padding=1, **kwargs)

    def forward(self, x):
        skipco = self.skip_cos.pop()
        x = self.shuf(x)
        ssh = skipco.shape[-2:]
        if ssh != x.shape[-2:]:
            x = interpolate(x, ssh, mode='nearest')
        x = self.relu(torch.cat([x, self.bn(skipco)], dim=1))
        return self.conv2(self.conv1(x))

#Cell
def _get_sizes(model, input_shape=(3, 224, 224)):
    sizes = []
    size_handles = []
    leaf_modules = named_leaf_modules('', model)

    def _hook(model, input, output):
        sizes.append((model, input[0].shape[1:], output.shape[1:]))

    for n, m in leaf_modules:
        m.name = n
        size_handles.append(m.register_forward_hook(_hook))

    x = torch.rand(2, *input_shape)
    model.eval()(x)
    for handle in size_handles:
        handle.remove()
    return np.array(sizes)

#Cell
class DynamicUnet(nn.Module):
    def __init__(self, encoder_name, cut=-2, n_classes=2, input_shape=(3, 224, 224), pretrained=True):
        super(DynamicUnet, self).__init__()
        encoder = timm.create_model(encoder_name, pretrained=pretrained)
        self.encoder = nn.Sequential(*(list(encoder.children())[:cut]+[nn.ReLU()]))
        encoder_sizes, idxs = self.register_output_hooks(input_shape=input_shape)
        n_chans = encoder_sizes[-1, 2][0]
        middle_conv = nn.Sequential(ConvBnRelu(n_chans, n_chans//2, 3),
                                    ConvBnRelu(n_chans//2, n_chans, 3))
        decoder = [middle_conv]
        for k, idx in enumerate(idxs[::-1]):
            skip_chans = encoder_sizes[idx, 1][0]
            final_div = (k != len(idxs)-1)
            decoder.append(DecoderBlock(n_chans, skip_chans, self.skip_cos, final_div=final_div))
            n_chans = n_chans//2 + skip_chans
            n_chans = n_chans if not final_div else skip_chans
        self.decoder = nn.Sequential(*decoder, ConvBn(n_chans, n_classes, 1))


    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


    def register_output_hooks(self, input_shape=(3, 224, 224)):
        sizes = get_sizes(self.encoder, input_shape=input_shape)
        self.skip_cos = []
        self.handles = []
        idxs = []

        def _hook(model, input, output):
            self.skip_cos.append(input[0])

        for k, (m, in_shape, out_shape) in enumerate(sizes):
            if len(out_shape) == len(in_shape) == 3 and out_shape[1] != in_shape[1] and 'downsample' not in m.name:
                self.handles.append(m.register_forward_hook(_hook))
                idxs.append(k)

        return sizes, idxs