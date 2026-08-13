# 🎨 Local Text-to-Image Generator

A fully local text-to-image generation app built with **PyTorch**, **Diffusers**, and **Gradio**. Generate images from text using open-source models — fully offline, no data leaves your machine.

## Features

- 🎨 Generate images from text prompts (text-to-image)
- 🖼️ Modify existing images (image-to-image)
- ✏️ Edit specific parts of images (inpainting)
- 🔀 Model picker — switch between multiple open-source models
- 🖼️ Multiple image generation with preview gallery
- 💾 Save selected images to disk
- ⚙️ Adjustable parameters (steps, guidance, size, seed, strength)
- 🎯 Automatic parameter recommendations per model
- 🔒 100% offline inference

## Hardware Requirements

**Minimum:** 16 GB RAM + 8 GB VRAM (for SD 1.5 models)
**Recommended:** 32 GB RAM + 16 GB VRAM (for SDXL and Flux models)

## Available Models

### Stable Diffusion 1.5 (4 GB VRAM) — Fast & Efficient

| Model | Category | Capabilities | Notes |
|-------|----------|--------------|-------|
| **SD-1.5** | General | txt2img, img2img | Classic SD 1.5 - fast, low VRAM, great for quick iterations |
| **SD-1.5-Inpainting** | General | inpaint | Edit parts of images with inpainting |
| **OpenJourney** | Artistic | txt2img, img2img | Midjourney-style artistic images |
| **DreamShaper** | Artistic | txt2img, img2img | High-quality illustrations |
| **RealisticVision** | Photorealistic | txt2img, img2img | Best for portraits and realistic scenes |
| **AnythingV5** | Anime | txt2img, img2img | Excellent anime/manga art |

### Stable Diffusion XL (8 GB VRAM) — High Quality

| Model | Category | Capabilities | Notes |
|-------|----------|--------------|-------|
| **SDXL-1.0** | General | txt2img, img2img | High quality 1024x1024 images |
| **SDXL-Turbo** | General | txt2img, img2img | Fast 1-step generation |
| **JuggernautXL** | Photorealistic | txt2img, img2img | Stunning portraits and scenes |
| **AnimagineXL** | Anime | txt2img, img2img | Best anime SDXL model |

### Flux (12 GB VRAM) — Best Quality

| Model | Category | Capabilities | Notes |
|-------|----------|--------------|-------|
| **Flux.1-Schnell** | General | txt2img | Fast 4-step generation, excellent quality |
| **Flux.1-Dev** | General | txt2img | Highest quality (gated — needs HF token) |

### Kandinsky (6 GB VRAM) — Alternative

| Model | Category | Capabilities | Notes |
|-------|----------|--------------|-------|
| **Kandinsky-2.2** | Artistic | txt2img, img2img | Artistic, creative images |

## Installation

Python 3.10–3.12 recommended. Linux (or WSL2 on Windows) gives the smoothest experience.

```bash
# 1. Create an environment
conda create --name local_imagegen python=3.10
conda activate local_imagegen

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

Open http://127.0.0.1:7860, pick a model, press **Load model**, and start generating!

## Usage

### Text-to-Image

1. **Select a model** from the dropdown
2. **Load the model** (first time will take a moment)
3. **Enter a prompt** describing the image you want
4. **(Optional)** Add a negative prompt to avoid certain features
5. **Adjust parameters** if needed (steps, guidance, size)
6. **Click Generate** — images will appear in the gallery
7. **Select images** you want to save
8. **Click Save Selected** — images are saved to `./generated_images/`

### Image-to-Image

1. **Select a model** that supports img2img (e.g., SD-1.5, SDXL-1.0)
2. **Load the model**
3. **Open "Reference Image" accordion**
4. **Upload an image** you want to modify
5. **Enter a prompt** describing the changes
6. **Adjust strength** (0.5 = subtle, 0.8 = moderate, 1.0 = dramatic)
7. **Click Generate**

### Inpainting

1. **Select SD-1.5-Inpainting** (or another inpainting model)
2. **Load the model**
3. **Open "Reference Image" accordion**
4. **Upload the image** you want to edit
5. **Upload a mask image** (white = change, black = keep)
   - You can create masks in Photoshop, GIMP, or any image editor
   - Or use online tools like [maskmaker.ai](https://maskmaker.ai)
6. **Enter a prompt** for what to add/change in the masked area
7. **Click Generate**

## Model Recommendations

### For Text-to-Image:
- **Quick iterations**: SD-1.5 (fast, low VRAM)
- **Photorealistic portraits**: RealisticVision or JuggernautXL
- **Anime art**: AnythingV5 or AnimagineXL
- **Best quality**: Flux.1-Schnell (if you have 12+ GB VRAM)
- **Artistic images**: DreamShaper or Kandinsky-2.2

### For Image-to-Image:
- **Style transfer**: SD-1.5 or DreamShaper
- **Photo enhancement**: RealisticVision
- **Anime modification**: AnythingV5 or AnimagineXL
- **High quality edits**: SDXL-1.0

### For Inpainting:
- **Object removal**: SD-1.5-Inpainting
- **Object addition**: SD-1.5-Inpainting
- **Background changes**: SD-1.5-Inpainting

## Tips for Best Results

### Text-to-Image:
- **SD 1.5**: Use 512x512, 50 steps, guidance 7.5
- **SDXL**: Use 1024x1024, 30 steps, guidance 7.5
- **Flux**: Use 1024x1024, 4 steps, guidance 3.5
- **Negative prompts**: Add "blurry, low quality, distorted, ugly" to avoid common issues
- **Seeds**: Use the same seed to reproduce results, or -1 for random

### Image-to-Image:
- **Strength 0.3-0.5**: Subtle changes, keeps original composition
- **Strength 0.6-0.8**: Moderate changes, good balance
- **Strength 0.9-1.0**: Dramatic changes, almost like new generation
- **Prompt**: Be specific about what you want to change

### Inpainting:
- **Mask quality**: Clean, sharp edges work best
- **Mask size**: Larger masks give more flexibility
- **Prompt**: Describe what should appear in the masked area
- **Blending**: Use feathered mask edges for better blending

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

## Example Workflows

### 1. Transform a Photo into Anime
1. Load AnythingV5
2. Upload your photo in "Reference Image"
3. Set strength to 0.75
4. Prompt: "anime style, detailed, vibrant colors"
5. Generate

### 2. Remove an Object from a Photo
1. Load SD-1.5-Inpainting
2. Upload the photo
3. Create a mask covering the object (white on object, black elsewhere)
4. Upload the mask
5. Prompt: "empty background, seamless"
6. Generate

### 3. Add a Sunset to a Landscape
1. Load SDXL-1.0
2. Upload your landscape photo
3. Set strength to 0.6
4. Prompt: "beautiful sunset, golden hour, dramatic sky"
5. Generate

### 4. Change Clothing Style
1. Load RealisticVision
2. Upload portrait photo
3. Create mask over clothing
4. Upload mask
5. Prompt: "elegant dress, formal wear, high fashion"
6. Generate

## Troubleshooting

- **CUDA out of memory** → Use a smaller model (SD 1.5 instead of SDXL), reduce image size, or close other GPU apps
- **Model fails to load** → Make sure you've downloaded it first: `python download_models.py --models "ModelName"`
- **Slow generation** → Reduce inference steps or image size
- **Poor quality** → Increase inference steps, adjust guidance scale, or try a different model
- **Flux models not working** → Make sure you have 12+ GB VRAM and are using bf16
- **Img2img not working** → Make sure the model supports it (check model info accordion)
- **Inpainting artifacts** → Use cleaner masks with softer edges, adjust strength lower

## Adding a New Model

1. Add an entry to `MODEL_REGISTRY` in `model_registry.py`:
   ```python
   "MyModel": {
       "repo_id": "username/model-name",
       "kind": "sd",  # or "sdxl", "flux", "kandinsky", "inpaint"
       "category": "general",
       "vram_gb": 4.0,
       "gated": False,
       "notes": "Description here",
       "supports": ["txt2img", "img2img"],  # or ["inpaint"]
   }
   ```
2. Run `python download_models.py --models "MyModel"`
3. Select it in the UI

## Licenses

The app code is yours to use freely. Model weights are governed by their own licenses:
- **SD 1.5 / SDXL**: CreativeML Open RAIL-M
- **Flux**: Apache 2.0 (Schnell), Flux License (Dev)
- **Kandinsky**: Apache 2.0
- **DreamShaper, RealisticVision, etc.**: Check individual model licenses

Review them before redistribution or commercial use.

## Resources

- **Prompt ideas**: [PromptHero](https://prompthero.com)
- **Mask creation**: [maskmaker.ai](https://maskmaker.ai)
- **Model browsing**: [Hugging Face Diffusers](https://huggingface.co/models?pipeline_tag=text-to-image)
- **Community**: [r/StableDiffusion](https://reddit.com/r/StableDiffusion)