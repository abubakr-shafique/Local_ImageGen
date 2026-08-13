"""Image generation using PyTorch and Diffusers.

This module handles loading text-to-image models and generating images.
Supports Stable Diffusion, SDXL, Flux, and Kandinsky models.
"""
import gc
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from PIL import Image

from model_registry import MODEL_REGISTRY, MODELS_DIR, get_model_kind

# Model type to pipeline class mapping
PIPELINE_MAP = {
    "sd": "StableDiffusionPipeline",
    "sdxl": "StableDiffusionXLPipeline",
    "flux": "FluxPipeline",
    "kandinsky": "KandinskyV22Pipeline",
}


class ImageGenerator:
    """Manages a single loaded image generation model."""

    def __init__(self):
        self.pipeline = None
        self.current_key: Optional[str] = None
        self.kind: Optional[str] = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    @staticmethod
    def is_downloaded(key: str) -> bool:
        """Check if model weights exist locally."""
        model_path = MODELS_DIR / key
        return model_path.exists() and any(model_path.iterdir())

    @staticmethod
    def _vram_gb() -> float:
        """Return current VRAM usage in GB (0.0 if CUDA unavailable)."""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024 ** 3
        return 0.0

    def load(self, key: str) -> str:
        """Load a model by registry key.

        Returns a status message string.
        """
        if key not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model '{key}'.")
        if self.current_key == key:
            return f"✅ **{key}** is already loaded."
        if not self.is_downloaded(key):
            raise FileNotFoundError(
                f"Weights for '{key}' not found at `{MODELS_DIR / key}`.\n\n"
                f"Download them first:\n```\npython download_models.py --models \"{key}\"\n```"
            )

        self.unload()
        cfg = MODEL_REGISTRY[key]
        path = str(MODELS_DIR / key)
        kind = cfg["kind"]

        try:
            # Import appropriate pipeline
            if kind == "sd":
                from diffusers import StableDiffusionPipeline
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    path,
                    torch_dtype=self.dtype,
                    safety_checker=None,
                    requires_safety_checker=False,
                )
            elif kind == "sdxl":
                from diffusers import StableDiffusionXLPipeline
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                    path,
                    torch_dtype=self.dtype,
                    use_safetensors=True,
                )
            elif kind == "flux":
                from diffusers import FluxPipeline
                self.pipeline = FluxPipeline.from_pretrained(
                    path,
                    torch_dtype=torch.bfloat16,  # Flux works better with bf16
                )
            elif kind == "kandinsky":
                from diffusers import KandinskyV22Pipeline
                self.pipeline = KandinskyV22Pipeline.from_pretrained(
                    path,
                    torch_dtype=self.dtype,
                )
            else:
                raise ValueError(f"Unsupported model kind: {kind}")

            # Move to device
            self.pipeline = self.pipeline.to(self.device)

            # Enable memory optimizations
            if hasattr(self.pipeline, "enable_attention_slicing"):
                self.pipeline.enable_attention_slicing()
            if hasattr(self.pipeline, "enable_vae_slicing"):
                self.pipeline.enable_vae_slicing()

            self.current_key = key
            self.kind = kind

            vram = self._vram_gb()
            return f"✅ Loaded **{key}** — {vram:.1f} GiB VRAM in use."

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def unload(self) -> str:
        """Unload the current model and free GPU memory."""
        self.pipeline = None
        self.current_key = None
        self.kind = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return "🗑️ Model unloaded."

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        num_images: int = 1,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512,
        seed: Optional[int] = None,
    ) -> Tuple[List[Image.Image], str]:
        """Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            negative_prompt: Text describing what to avoid in the image.
            num_images: Number of images to generate.
            num_inference_steps: Number of denoising steps.
            guidance_scale: How closely to follow the prompt.
            width: Image width in pixels.
            height: Image height in pixels.
            seed: Random seed for reproducibility.

        Returns:
            Tuple of (list of PIL Images, status message).
        """
        if self.pipeline is None:
            raise RuntimeError("No model loaded.")

        # Set seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)

        # Adjust parameters based on model type
        if self.kind == "flux":
            # Flux uses different parameters
            num_inference_steps = min(num_inference_steps, 4)  # Flux works best with few steps
            guidance_scale = 3.5  # Flux default
        elif self.kind == "sdxl":
            # SDXL prefers 1024x1024
            if width < 1024:
                width = 1024
            if height < 1024:
                height = 1024

        try:
            # Generate images
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt if negative_prompt else None,
                num_images_per_prompt=num_images,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=generator,
            )

            images = result.images
            msg = f"✅ Generated {len(images)} image(s) with **{self.current_key}**"
            return images, msg

        except Exception as e:
            raise RuntimeError(f"Generation failed: {e}")

    def get_recommended_params(self) -> Dict[str, Any]:
        """Get recommended generation parameters for the current model."""
        if self.kind == "flux":
            return {
                "num_inference_steps": 4,
                "guidance_scale": 3.5,
                "width": 1024,
                "height": 1024,
            }
        elif self.kind == "sdxl":
            return {
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024,
            }
        elif self.kind == "kandinsky":
            return {
                "num_inference_steps": 50,
                "guidance_scale": 4.0,
                "width": 512,
                "height": 512,
            }
        else:  # sd
            return {
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512,
            }