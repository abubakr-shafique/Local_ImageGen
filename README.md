# 🎨 Local Text-to-Image Generator

A fully local text-to-image generation app built with **PyTorch**, **Diffusers**, and **Gradio**. Generate images from text using open-source models — fully offline, no data leaves your machine.

## Features

- 🎨 Generate images from text prompts
- 🔀 Model picker — switch between multiple open-source models
- 🖼️ Multiple image generation with preview gallery
- 💾 Save selected images to disk
- ⚙️ Adjustable parameters (steps, guidance, size, seed)
- 🎯 Automatic parameter recommendations per model
- 🔒 100% offline inference

## Hardware Requirements

**Minimum:** 16 GB RAM + 8 GB VRAM (for SD 1.5 models)
**Recommended:** 32 GB RAM + 16 GB VRAM (for SDXL and Flux models)

## Available Models

### Stable Diffusion 1.5 (4 GB VRAM) — Fast & Efficient

| Model | Category | Notes |
|-------|----------|-------|
| **SD-1.5** | General | Classic SD 1.5 - fast, low VRAM, great for quick iterations |
| **SD-1.5-Inpainting** | General | Edit parts of images with inpainting |
| **OpenJourney** | Artistic | Midjourney-style artistic images |
| **DreamShaper** | Artistic | High-quality illustrations |
| **RealisticVision** | Photorealistic | Best for portraits and realistic scenes |
| **AnythingV5** | Anime | Excellent anime/manga art |

### Stable Diffusion XL (8 GB VRAM) — High Quality

| Model | Category | Notes |
|-------|----------|-------|
| **SDXL-1.0** | General | High quality 1024x1024 images |
| **SDXL-Turbo** | General | Fast 1-step generation |
| **JuggernautXL** | Photorealistic | Stunning portraits and scenes |
| **AnimagineXL** | Anime | Best anime SDXL model |

### Flux (12 GB VRAM) — Best Quality

| Model | Category | Notes |
|-------|----------|-------|
| **Flux.1-Schnell** | General | Fast 4-step generation, excellent quality |
| **Flux.1-Dev** | General | Highest quality (gated — needs HF token) |

### Kandinsky (6 GB VRAM) — Alternative

| Model | Category | Notes |
|-------|----------|-------|
| **Kandinsky-2.2** | Artistic | Artistic, creative images |

## Installation

Python 3.10–3.12 recommended. Linux (or WSL2 on Windows) gives the smoothest experience.

```bash
# 1. Create an environment
conda create --name local_ImageGen python=3.10
conda activate local_ImageGen

# 2. Install PyTorch with CUDA (pick the wheel matching your driver)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 3. Install the rest
pip install -r requirements.txt
```

## Downloading Models

Weights are stored locally in `./models/` (override with the `IMAGEGEN_MODELS_DIR` env var).

```bash
python download_models.py --list                    # show all models
python download_models.py --models "SD-1.5"         # download one
python download_models.py --models "SD-1.5" "SDXL-1.0"  # download multiple
python download_models.py                           # download all
```

**Gated models** (Flux.1-Dev) require a free Hugging Face account: accept the license on the model's HF page, then run `huggingface-cli login` with an access token before downloading.

## Running

```bash
python app.py
```

Open http://127.0.0.1:7860, pick a model, press **Load model**, enter a prompt, and click **Generate Images**.

## Usage

1. **Select a model** from the dropdown
2. **Load the model** (first time will take a moment)
3. **Enter a prompt** describing the image you want
4. **(Optional)** Add a negative prompt to avoid certain features
5. **Adjust parameters** if needed (steps, guidance, size)
6. **Click Generate** — images will appear in the gallery
7. **Select images** you want to save
8. **Click Save Selected** — images are saved to `./generated_images/`

## Model Recommendations

- **Quick iterations**: SD-1.5 (fast, low VRAM)
- **Photorealistic portraits**: RealisticVision or JuggernautXL
- **Anime art**: AnythingV5 or AnimagineXL
- **Best quality**: Flux.1-Schnell (if you have 12+ GB VRAM)
- **Artistic images**: DreamShaper or Kandinsky-2.2

## Project Structure

```
├── app.py                  # Gradio GUI (model picker, generation, gallery, save)
├── image_generator.py      # PyTorch/Diffusers backend: load/unload, generate
├── model_registry.py       # Registry of supported models + metadata
├── download_models.py      # One-shot weight downloader (Hugging Face → ./models)
├── requirements.txt
├── models/                 # Local weights live here (created by download_models.py)
└── generated_images/       # Saved images (created by app.py)
```

## Tips for Best Results

- **SD 1.5**: Use 512x512, 50 steps, guidance 7.5
- **SDXL**: Use 1024x1024, 30 steps, guidance 7.5
- **Flux**: Use 1024x1024, 4 steps, guidance 3.5
- **Negative prompts**: Add "blurry, low quality, distorted, ugly" to avoid common issues
- **Seeds**: Use the same seed to reproduce results, or -1 for random

## Troubleshooting

- **CUDA out of memory** → Use a smaller model (SD 1.5 instead of SDXL), reduce image size, or close other GPU apps
- **Model fails to load** → Make sure you've downloaded it first: `python download_models.py --models "ModelName"`
- **Slow generation** → Reduce inference steps or image size
- **Poor quality** → Increase inference steps, adjust guidance scale, or try a different model
- **Flux models not working** → Make sure you have 12+ GB VRAM and are using bf16

## Adding a New Model

1. Add an entry to `MODEL_REGISTRY` in `model_registry.py`:
   ```python
   "MyModel": {
       "repo_id": "username/model-name",
       "kind": "sd",  # or "sdxl", "flux", "kandinsky"
       "category": "general",
       "vram_gb": 4.0,
       "gated": False,
       "notes": "Description here",
   }
   ```
2. Run `python download_models.py --models "MyModel"`
3. Select it in the UI

## Licenses

The app code is yours to use freely. Model weights are governed by their own licenses:
- **SD 1.5 / SDXL**: CreativeML Open RAIL-M
- **Flux**: Apache 2.0 (Schnell), Flux License (Dev)
- **Kandinsky**: Apache 2.0

Review them before redistribution or commercial use.