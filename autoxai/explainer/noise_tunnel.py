"""File with Noise Tunnel algorithm explainer classes.

Based on https://github.com/pytorch/captum/blob/master/captum/attr/_core/noise_tunnel.py.
"""

from abc import abstractmethod
from typing import Optional, Tuple, Union

import torch
from captum._utils.typing import TargetType
from captum.attr import IntegratedGradients, LayerIntegratedGradients, NoiseTunnel

from autoxai.array_utils import validate_result
from autoxai.explainer.base_explainer import CVExplainer
from autoxai.explainer.model_utils import get_last_conv_model_layer


class BaseNoiseTunnelCVExplainer(CVExplainer):
    """Base Noise Tunnel algorithm explainer."""

    @abstractmethod
    def create_explainer(self, model: torch.nn.Module, **kwargs) -> NoiseTunnel:
        """Create explainer object.

        Args:
            model: The forward function of the model or any
                modification of it.

        Returns:
            Explainer object.
        """

    def calculate_features(
        self,
        model: torch.nn.Module,
        input_data: torch.Tensor,
        pred_label_idx: TargetType = None,
        nt_type: str = "smoothgrad",
        nt_samples: int = 5,
        nt_samples_batch_size: int = None,
        stdevs: Union[float, Tuple[float, ...]] = 1.0,
        draw_baseline_from_distrib: bool = False,
        **kwargs,
    ) -> torch.Tensor:
        """Generate model's attributes with Noise Tunnel algorithm explainer.

        Args:
            model: The forward function of the model or any
                modification of it.
            input_data: Input for which integrated
                gradients are computed. If forward_func takes a single
                tensor as input, a single input tensor should be provided.
            pred_label_idx: Output indices for
                which gradients are computed (for classification cases,
                this is usually the target class).
                If the network returns a scalar value per example,
                no target index is necessary.
                For general 2D outputs, targets can be either:

                - a single integer or a tensor containing a single
                    integer, which is applied to all input examples

                - a list of integers or a 1D tensor, with length matching
                    the number of examples in inputs (dim 0). Each integer
                    is applied as the target for the corresponding example.

                For outputs with > 2 dimensions, targets can be either:

                - A single tuple, which contains #output_dims - 1
                    elements. This target index is applied to all examples.

                - A list of tuples with length equal to the number of
                    examples in inputs (dim 0), and each tuple containing
                    #output_dims - 1 elements. Each tuple is applied as the
                    target for the corresponding example.

                Default: None
            nt_type: Smoothing type of the attributions.
                `smoothgrad`, `smoothgrad_sq` or `vargrad`
                Default: `smoothgrad` if `type` is not provided.
            nt_samples: The number of randomly generated examples
                per sample in the input batch. Random examples are
                generated by adding gaussian random noise to each sample.
                Default: `5` if `nt_samples` is not provided.
            nt_samples_batch_size: The number of the `nt_samples`
                that will be processed together. With the help
                of this parameter we can avoid out of memory situation and
                reduce the number of randomly generated examples per sample
                in each batch.
                Default: None if `nt_samples_batch_size` is not provided. In
                this case all `nt_samples` will be processed together.
            stdevs: The standard deviation
                of gaussian noise with zero mean that is added to each
                input in the batch. If `stdevs` is a single float value
                then that same value is used for all inputs. If it is
                a tuple, then it must have the same length as the inputs
                tuple. In this case, each stdev value in the stdevs tuple
                corresponds to the input with the same index in the inputs
                tuple.
                Default: `1.0` if `stdevs` is not provided.
            draw_baseline_from_distrib: Indicates whether to
                randomly draw baseline samples from the `baselines`
                distribution provided as an input tensor.
                Default: False

        Returns:
            Attribution with respect to each input feature. attributions
            will always be the same size as the provided inputs, with each value
            providing the attribution of the corresponding input index.
            If a single tensor is provided as inputs, a single tensor is
            returned.

        Raises:
            RuntimeError: if attribution has shape (0).
        """
        layer: Optional[torch.nn.Module] = kwargs.get("layer", None)

        noise_tunnel = self.create_explainer(model=model, layer=layer)

        attributions = noise_tunnel.attribute(
            input_data,
            nt_samples=nt_samples,
            nt_type=nt_type,
            target=pred_label_idx,
            nt_samples_batch_size=nt_samples_batch_size,
            stdevs=stdevs,
            draw_baseline_from_distrib=draw_baseline_from_distrib,
        )
        validate_result(attributions=attributions)
        return attributions


class NoiseTunnelCVExplainer(BaseNoiseTunnelCVExplainer):
    """Noise Tunnel algorithm explainer."""

    def create_explainer(
        self,
        model: torch.nn.Module,
        **kwargs,
    ) -> NoiseTunnel:
        """Create explainer object.

        Args:
            model: The forward function of the model or any
                modification of it.

        Returns:
            Explainer object.
        """
        integrated_gradients = IntegratedGradients(forward_func=model)
        return NoiseTunnel(integrated_gradients)


class LayerNoiseTunnelCVExplainer(BaseNoiseTunnelCVExplainer):
    """Layer Noise Tunnel algorithm explainer."""

    def create_explainer(
        self,
        model: torch.nn.Module,
        layer: Optional[torch.nn.Module] = None,
        **kwargs,
    ) -> NoiseTunnel:
        """Create explainer object.

        Uses parameter `layer` from `kwargs`. If not provided function will call
        `get_last_conv_model_layer` function to obtain last `torch.nn.Conv2d` layer
        from provided model.

        Args:
            model: The forward function of the model or any
                modification of it.
            layer: Layer for which attributions are computed.
                Output size of attribute matches this layer's input or
                output dimensions, depending on whether we attribute to
                the inputs or outputs of the layer, corresponding to
                attribution of each neuron in the input or output of
                this layer.
                Default: None

        Returns:
            Explainer object.

        Raises:
            ValueError: if model does not contain conv layers.
        """
        if layer is None:
            layer = get_last_conv_model_layer(model=model)

        integrated_gradients = LayerIntegratedGradients(forward_func=model, layer=layer)
        return NoiseTunnel(integrated_gradients)
