"""Registry of supported open-source text-to-image and image-to-image models.

Add new models by adding an entry to MODEL_REGISTRY:
- repo_id: Hugging Face repo id (weights are downloaded from here)
- kind: "sd" (Stable Diffusion), "sdxl" (SDXL), "flux" (Flux), "kandinsky" (Kandinsky)
- category: "general" | "anime" | "photorealistic" | "artistic" | "img2img" (display grouping)
- vram_gb: rough VRAM estimate at fp16/bf16 (for the UI)
- gated: True if the HF repo requires accepting a license + token
- notes: short description shown in docs
- supports: List of capabilities ["txt2img"], ["txt2img", "img2img"], ["inpaint"]
"""
import os
from pathlib import Path

MODELS_DIR = Path(os.environ.get("IMAGEGEN_MODELS_DIR", Path(__file__).parent / "models"))

MODEL_REGISTRY = {
    # ---------------- Stable Diffusion 1.5 (fast, low VRAM) ----------------
    "SD-1.5": {
        "repo_id": "runwayml/stable-diffusion-v1-5",
        "kind": "sd",
        "category": "general",
        "vram_gb": 4.0,
        "gated": False,
        "notes": "Classic SD 1.5 - fast, low VRAM, great for quick iterations.",
        "supports": ["txt2img", "img2img"],
    },
    "SD-1.5-Inpainting": {
        "repo_id": "runwayml/stable-diffusion-inpainting",
        "kind": "sd",
        "category": "general",
        "vram_gb": 4.0,
        "gated": False,
        "notes": "SD 1.5 with inpainting support - edit parts of images.",
        "supports": ["txt2img", "img2img", "inpaint"],
    },
    "OpenJourney": {
        "repo_id": "prompthero/openjourney",
        "kind": "sd",
        "category": "artistic",
        "vram_gb": 4.0,
        "gated": False,
        "notes": "Midjourney-style fine-tuned SD 1.5 - artistic images.",
        "supports": ["txt2img", "img2img"],
    },
    "DreamShaper": {
        "repo_id": "Lykon/DreamShaper",
        "kind": "sd",
        "category": "artistic",
        "vram_gb": 4.0,
        "gated": False,
        "notes": "High-quality artistic model - great for illustrations.",
        "supports": ["txt2img", "img2img"],
    },
    "RealisticVision": {
        "repo_id": "SG161222/Realistic_Vision_V5.1_noVAE",
        "kind": "sd",
        "category": "photorealistic",
        "vram_gb": 4.0,
        "gated": False,
        "notes": "Photorealistic images - best for portraits and scenes.",
        "supports": ["txt2img", "img2img"],
    },
    "AnythingV5": {
        "repo_id": "stablediffusionapi/anything-v5",
        "kind": "sd",
        "category": "anime",
        "vram_gb": 4.0,
        "gated": False,
        "notes": "Anime-style images - excellent for anime/manga art.",
        "supports": ["txt2img", "img2img"],
    },
    
    # ---------------- Stable Diffusion XL (high quality) ----------------
    "SDXL-1.0": {
        "repo_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "kind": "sdxl",
        "category": "general",
        "vram_gb": 8.0,
        "gated": False,
        "notes": "SDXL base - high quality 1024x1024 images, needs more VRAM.",
        "supports": ["txt2img", "img2img"],
    },
    "SDXL-Turbo": {
        "repo_id": "stabilityai/sdxl-turbo",
        "kind": "sdxl",
        "category": "general",
        "vram_gb": 8.0,
        "gated": False,
        "notes": "SDXL Turbo - fast 1-step generation, good quality.",
        "supports": ["txt2img", "img2img"],
    },
    "JuggernautXL": {
        "repo_id": "RunDiffusion/Juggernaut-XL-v9",
        "kind": "sdxl",
        "category": "photorealistic",
        "vram_gb": 8.0,
        "gated": False,
        "notes": "Photorealistic SDXL - stunning portraits and scenes.",
        "supports": ["txt2img", "img2img"],
    },
    "AnimagineXL": {
        "repo_id": "cagliostrolab/animagine-xl-3.1",
        "kind": "sdxl",
        "category": "anime",
        "vram_gb": 8.0,
        "gated": False,
        "notes": "Best anime SDXL model - high quality anime art.",
        "supports": ["txt2img", "img2img"],
    },
    
    # ---------------- Flux (best quality, high VRAM) ----------------
    "Flux.1-Schnell": {
        "repo_id": "black-forest-labs/FLUX.1-schnell",
        "kind": "flux",
        "category": "general",
        "vram_gb": 12.0,
        "gated": False,
        "notes": "Flux Schnell - fast 4-step generation, excellent quality.",
        "supports": ["txt2img"],
    },
    "Flux.1-Dev": {
        "repo_id": "black-forest-labs/FLUX.1-dev",
        "kind": "flux",
        "category": "general",
        "vram_gb": 12.0,
        "gated": True,
        "notes": "Flux Dev - highest quality, needs license acceptance.",
        "supports": ["txt2img"],
    },
    
    # ---------------- Kandinsky (alternative) ----------------
    "Kandinsky-2.2": {
        "repo_id": "kandinsky-community/kandinsky-2-2-decoder",
        "kind": "kandinsky",
        "category": "artistic",
        "vram_gb": 6.0,
        "gated": False,
        "notes": "Kandinsky 2.2 - artistic, good for creative images.",
        "supports": ["txt2img", "img2img"],
    },
}

DEFAULT_MODEL = "SD-1.5"


def get_model_kind(model_key: str) -> str:
    """Return the model kind (sd, sdxl, flux, kandinsky)."""
    cfg = MODEL_REGISTRY.get(model_key)
    if cfg is None:
        return "unknown"
    return cfg.get("kind", "unknown")


def get_model_category(model_key: str) -> str:
    """Return the model category (general, anime, photorealistic, artistic)."""
    cfg = MODEL_REGISTRY.get(model_key)
    if cfg is None:
        return "unknown"
    return cfg.get("category", "unknown")


def model_supports(model_key: str, capability: str) -> bool:
    """Check if model supports a specific capability (txt2img, img2img, inpaint)."""
    cfg = MODEL_REGISTRY.get(model_key)
    if cfg is None:
        return False
    supports = cfg.get("supports", ["txt2img"])
    return capability in supports