# pylint: disable = missing-class-docstring
import logging

import numpy as np
import pytest
import torch
from torch.nn import functional as F
from torchvision import transforms

from autoxai.context_manager import AutoXaiExplainer, Explainers

w = [255, 255, 255]
c = [0, 0, 0]
h = [50, 50, 50]
g = [90, 90, 90]
f = [139, 69, 19]
a = [255, 232, 122]
b = [255, 210, 100]
d = [205, 133, 63]
e = [255, 165, 0]
i = [255, 255, 153]
j = [255, 0, 0]

# fmt: off
# pylint: disable = line-too-long
pikachu_image: np.ndarray = np.array([
    [w, w, w, w, c, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, h, c, w, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, h, c, w, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, h, h, c, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, h, h, h, c, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, h, h, h, f, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, h, g, b, f, w, w, w,   w, w, w, w, w, w, w, w, w, w,    w, w, w, w, h, h, h, h, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, g, b, b, b, f, w, w,   w, w, w, w, w, w, w, w, w, w,    w, h, h, h, g, g, g, g, h, c,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, b, b, b, b, f, w, w,   w, w, w, w, w, w, w, w, w, d,    d, b, a, a, g, g, g, g, g, c,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, b, b, b, b, f, w, w,   d, d, d, d, w, w, w, d, d, a,    a, a, a, a, g, g, g, g, c, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, f, b, b, b, d, d, e,   i, i, i, a, a, e, d, a, a, a,    a, a, a, g, g, g, g, c, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, f, b, b, e, e, i, i,   i, i, i, i, a, a, a, a, a, a,    a, a, a, g, g, c, c, w, w, w,   w, w, w, w, d, d, w, w, w, w],
    [w, w, w, w, f, e, a, i, i, i,   i, i, i, a, a, a, a, a, a, a,    a, a, c, c, c, w, w, w, w, w,   w, w, w, d, a, a, d, w, w, w],
    [w, w, w, w, d, a, a, a, a, a,   a, a, a, b, c, c, b, a, a, e,    d, c, w, w, w, w, w, w, w, w,   w, w, d, a, a, a, a, d, w, w],
    [w, w, w, f, e, c, b, a, a, a,   a, a, a, g, w, c, h, a, a, a,    c, w, w, w, w, w, w, w, w, w,   w, e, a, a, a, a, a, d, w, w],
    [w, w, w, f, c, w, b, a, a, a,   a, a, a, c, c, g, h, a, a, a,    c, w, w, w, w, w, w, w, w, w,   e, a, a, a, a, a, a, a, d, w],
    [w, w, w, f, g, c, a, a, f, e,   a, a, a, b, c, c, b, a, a, a,    d, w, w, w, w, w, w, w, e, e,   a, a, a, a, a, a, a, a, d, w],
    [w, w, w, d, h, d, a, a, a, a,   a, a, a, a, a, a, a, j, j, a,    e, f, w, w, w, w, w, d, a, a,   a, a, a, a, a, a, a, a, d, w],
    [w, w, f, a, a, a, a, a, f, d,   e, a, a, a, a, a, j, j, j, j,    b, c, w, w, w, w, d, a, a, a,   a, a, a, a, a, a, a, a, a, d],
    [w, w, f, j, b, a, e, f, d, b,   b, d, d, e, a, b, j, j, j, j,    b, c, w, w, w, d, a, a, a, a,   a, a, a, a, a, a, a, a, a, d],
    [w, w, f, j, b, b, b, b, b, b,   b, b, b, b, b, b, j, j, j, j,    b, c, w, w, w, d, b, a, a, a,   a, a, a, a, a, a, a, a, a, d],
    [w, w, f, b, b, b, b, b, b, b,   b, b, b, b, b, b, b, b, j, j,    b, c, w, w, d, b, b, b, b, a,   a, a, a, a, a, a, a, a, c, w],
    [w, w, w, d, b, b, b, b, b, b,   b, b, b, b, b, b, b, b, b, b,    b, c, w, d, b, b, b, b, b, b,   b, a, a, a, a, a, c, c, w, w],
    [w, w, w, w, c, b, b, b, b, b,   b, b, b, b, b, b, b, b, b, b,    b, f, w, d, b, b, b, b, b, b,   b, b, b, a, c, c, w, w, w, w],
    [w, w, w, w, c, b, b, b, b, b,   b, b, b, b, b, b, b, b, b, b,    b, a, c, d, f, b, b, b, b, b,   b, b, c, c, w, w, w, w, w, w],
    [w, w, w, w, c, a, b, b, b, b,   b, b, b, b, b, b, b, b, b, b,    a, a, c, w, w, f, b, b, b, b,   c, c, w, w, w, w, w, w, w, w],
    [w, w, w, w, c, a, a, a, b, b,   b, b, b, b, b, b, b, b, b, a,    a, a, c, w, w, w, f, b, b, d,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, w, c, a, a, a, a, a,   b, b, b, b, b, e, b, a, a, a,    a, a, c, w, w, w, w, f, b, b,   f, w, w, w, w, w, w, w, w, w],
    [w, w, w, w, c, a, a, d, a, a,   a, a, a, a, e, a, a, a, a, a,    a, a, f, w, w, w, c, e, b, b,   f, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, a, a, a, e, a, a,   a, a, a, a, e, a, a, a, a, a,    a, a, a, c, w, c, e, b, b, b,   b, f, w, w, w, w, w, w, w, w],
    [w, w, w, c, a, a, a, a, d, a,   a, a, a, d, a, a, a, a, a, b,    a, a, a, c, f, e, e, e, b, e,   f, c, w, w, w, w, w, w, w, w],
    [w, w, w, c, e, a, a, a, d, a,   a, a, a, d, a, a, a, a, b, e,    a, a, b, c, e, e, e, e, f, f,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, d, a, a, a, e, a,   a, a, d, a, a, a, a, a, d, e,    a, a, b, c, c, e, e, c, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, d, a, a, a, a, d,   a, a, c, e, a, a, a, d, a, a,    a, b, b, b, c, c, d, d, c, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, a, a, d, a, e, d, a,   a, a, a, c, a, e, d, a, a, a,    a, b, b, b, c, w, c, d, d, c,   w, w, w, w, w, w, w, w, w, w],
    [w, w, d, a, a, a, d, d, a, a,   a, a, a, a, d, d, a, a, a, a,    b, b, b, b, c, c, d, d, d, c,   w, w, w, w, w, w, w, w, w, w],
    [w, c, b, a, a, a, a, a, a, a,   a, a, a, a, a, a, a, a, b, a,    b, b, b, b, f, f, d, c, c, w,   w, w, w, w, w, w, w, w, w, w],
    [w, c, b, b, a, a, a, a, a, a,   a, a, a, a, a, a, a, b, a, b,    a, b, b, b, b, c, c, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, c, b, b, b, b, b, a, a, a,   a, a, a, a, b, b, b, a, b, a,    b, b, b, b, b, c, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, d, b, b, b, b, b, b, b,   b, b, b, b, b, b, b, b, b, b,    b, b, b, b, f, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, b, b, b, b, b, b, b,   b, b, b, b, b, b, b, b, b, b,    b, b, b, e, c, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, w, c, c, b, b, b, e, e,   c, c, c, c, f, b, b, b, b, b,    b, b, e, c, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, f, e, d, d, d, d, c,   w, w, w, w, w, c, f, d, d, e,    e, d, c, w, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, c, a, d, a, e, f, c, c, w,   w, w, w, w, w, w, w, w, f, b,    b, b, d, c, w, w, w, w, w, w,   w, w, w, w, w, w, w, w, w, w],
    [w, w, c, c, c, c, w, w, w, w,   w, w, w, w, w, w, w, w, w, w,    c, c, c, d, a, c, w, w, w, w,   w, w, w, w, w, w, w, w, w, w]],
    dtype=np.uint8,
)
# fmt: on


class SampleModel(torch.nn.Module):
    """Sample pytorch model for experiment."""

    def __init__(
        self,
        in_channels: int = 1,
        resolution: int = 224,
    ):
        super().__init__()
        self.stride: int = 16
        self.out_channels: int = 16
        self.conv1 = torch.nn.Conv2d(
            in_channels=in_channels,
            out_channels=self.out_channels,
            kernel_size=5,
            stride=16,
        )

        output_channels: int = ((resolution // self.stride) ** 2) * self.out_channels
        self.cls = torch.nn.Sequential(
            torch.nn.Dropout(),
            torch.nn.Linear(in_features=output_channels, out_features=1, bias=True),
        )
        self.sigmoid = torch.nn.Sigmoid()
        self.name = "SampleModel"

    def forward(self, x_tensor: torch.Tensor) -> torch.Tensor:
        """Forward methid for the module."""
        x_tensor = F.relu(self.conv1(x_tensor))
        x_tensor = x_tensor.view(x_tensor.size(0), -1)
        x_tensor = self.cls(x_tensor)
        x_tensor = self.sigmoid(x_tensor)
        return x_tensor


class TestAutoXaiExplainer:
    """Test whether context manager correctly
    switches model to eval mode and thows exception
    if no explainers provided.
    """

    @pytest.fixture
    def classifier(self) -> SampleModel:
        return SampleModel()

    def test_evel_mode(self, classifier: SampleModel, caplog: pytest.LogCaptureFixture):
        classifier.train()
        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Grayscale(),
                transforms.Resize(size=224),
                transforms.CenterCrop(size=224),
            ]
        )
        img_tensor: torch.Tensor = transform(pikachu_image).unsqueeze(0)
        caplog.set_level(level=logging.WARNING, logger="autoxai.context_manager")

        with torch.no_grad():
            with AutoXaiExplainer(
                model=classifier,
                explainers=[Explainers.CV_NOISE_TUNNEL_EXPLAINER],
            ) as xai_model:
                _, _ = xai_model(img_tensor)

                assert not xai_model.model.training
                assert "The model should be in the eval model" in caplog.text
