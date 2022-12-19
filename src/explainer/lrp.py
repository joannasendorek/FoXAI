"""File with LRP algorithm explainer classes."""

from abc import abstractmethod

import torch
from captum.attr import LRP, LayerLRP
from torch import fx

from src.explainer.base_explainer import CVExplainer
from src.explainer.model_utils import modify_modules


class BaseLRPCVExplainer(CVExplainer):
    """Base LRP algorithm explainer."""

    @abstractmethod
    def create_explainer(self, **kwargs):
        """Create explainer object.

        Raises:
            RuntimeError: When passed arguments are invalid.

        Returns:
            Explainer object.
        """

    def calculate_features(
        self,
        model: fx.GraphModule,
        input_data: torch.Tensor,
        pred_label_idx: int,
        **kwargs,
    ) -> torch.Tensor:
        """Generate features image with occulusion algorithm explainer.

        Args:
            model: Any DNN model You want to use.
            input_data: Input image.
            pred_label_idx: Predicted label.

        Returns:
            Features matrix.
        """
        layer: torch.nn.Module = kwargs.get("selected_layer", None)

        lrp = self.create_explainer(model=model, layer=layer)

        attributions = lrp.attribute(
            input_data,
            target=pred_label_idx,
        )
        return attributions


class LRPCVExplainer(BaseLRPCVExplainer):
    """LRP algorithm explainer."""

    def create_explainer(self, **kwargs):
        """Create explainer object.

        Raises:
            RuntimeError: When passed arguments are invalid.

        Returns:
            Explainer object.
        """
        model: fx.GraphModule = kwargs.get("model", None)
        if model is None:
            raise RuntimeError(f"Missing or `None` argument `model` passed: {kwargs}")

        model = modify_modules(model)

        return LRP(model=model)


class LayerLRPCVExplainer(BaseLRPCVExplainer):
    """Layer LRP algorithm explainer."""

    def create_explainer(self, **kwargs):
        """Create explainer object.

        Raises:
            RuntimeError: When passed arguments are invalid.

        Returns:
            Explainer object.
        """
        model: fx.GraphModule = kwargs.get("model", None)
        layer: torch.nn.Module = kwargs.get("layer", None)
        if model is None or layer is None:
            raise RuntimeError(
                f"Missing or `None` arguments `model` and `layer` passed: {kwargs}"
            )

        model = modify_modules(model)

        return LayerLRP(model=model, layer=layer)
