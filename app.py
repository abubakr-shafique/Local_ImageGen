"""Local text-to-image generation app — Gradio GUI.

Run: python app.py → http://127.0.0.1:7860

Features:
- Model selection with automatic parameter adjustment.
- Text-to-image, image-to-image, and inpainting.
- Multiple image generation with preview.
- Save selected images to disk.
- Adjustable generation parameters.
- Support for SD, SDXL, Flux, Kandinsky, img2img, and inpainting models.
"""
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
from PIL import Image

from image_generator import ImageGenerator
from model_registry import DEFAULT_MODEL, MODEL_REGISTRY, model_supports

generator = ImageGenerator()
OUTPUT_DIR = Path(__file__).parent / "generated_images"
OUTPUT_DIR.mkdir(exist_ok=True)

CATEGORY_LABELS = {
    "general": "General 🎨",
    "anime": "Anime 🌸",
    "photorealistic": "Photo 📷",
    "artistic": "Artistic 🖼️",
}


# --------------------------------------------------------------------- helpers
def model_status_markdown() -> str:
    """Generate a markdown summary of model download status."""
    lines = []
    for key, cfg in MODEL_REGISTRY.items():
        state = "✅ downloaded" if generator.is_downloaded(key) else "⬇️ not downloaded"
        tag = CATEGORY_LABELS.get(cfg.get("category", "general"), cfg["category"])
        supports = " | ".join(cfg.get("supports", ["txt2img"]))
        lines.append(
            f"- **{key}** ({tag}, ~{cfg['vram_gb']} GB VRAM) — {state} [{supports}]"
        )
    return "\n".join(lines)


def get_model_info(model_key: str) -> str:
    """Get information about a model."""
    cfg = MODEL_REGISTRY.get(model_key)
    if cfg is None:
        return "Unknown model"
    
    info = f"**{model_key}**\n\n"
    info += f"- Type: {cfg['kind']}\n"
    info += f"- Category: {cfg['category']}\n"
    info += f"- VRAM: ~{cfg['vram_gb']} GB\n"
    info += f"- Capabilities: {', '.join(cfg.get('supports', ['txt2img']))}\n"
    info += f"- {cfg['notes']}"
    return info


# ------------------------------------------------------------------- callbacks
def ui_load_model(key: str) -> Tuple[str, str]:
    """Load a model and return status messages."""
    try:
        msg = generator.load(key)
    except Exception as exc:
        msg = f"❌ {exc}"
    return msg, model_status_markdown()


def ui_unload_model() -> Tuple[str, str]:
    """Unload the current model and return status messages."""
    return generator.unload(), model_status_markdown()


def on_model_change(model_key: str) -> Dict[str, Any]:
    """Update UI based on selected model capabilities."""
    # Check model capabilities
    supports_img2img = model_supports(model_key, "img2img")
    supports_inpaint = model_supports(model_key, "inpaint")
    
    # Show/hide image upload based on capabilities
    return {
        image_upload: gr.update(visible=supports_img2img or supports_inpaint),
        mask_upload: gr.update(visible=supports_inpaint),
        strength_slider: gr.update(visible=supports_img2img or supports_inpaint),
    }


def generate_images(
    prompt: str,
    negative_prompt: str,
    reference_image: Optional[Dict[str, Any]],
    mask_image: Optional[Dict[str, Any]],
    num_images: int,
    num_inference_steps: int,
    guidance_scale: float,
    width: int,
    height: int,
    seed: Optional[int],
    strength: float,
) -> Tuple[List[Image.Image], str]:
    """Generate images and return them with a status message."""
    if not prompt.strip():
        return [], "⚠️ Please enter a prompt."
    
    if generator.pipeline is None:
        return [], "⚠️ No model is loaded. Select a model above and press **Load model**."
    
    # Process reference image
    ref_image = None
    if reference_image is not None and isinstance(reference_image, dict):
        if "path" in reference_image:
            try:
                ref_image = Image.open(reference_image["path"]).convert("RGB")
                print(f"Loaded reference image: {ref_image.size}")
            except Exception as e:
                print(f"Warning: Could not load reference image: {e}")
    
    # Process mask image
    mask_img = None
    if mask_image is not None and isinstance(mask_image, dict):
        if "path" in mask_image:
            try:
                mask_img = Image.open(mask_image["path"]).convert("RGB")
                print(f"Loaded mask image: {mask_img.size}")
            except Exception as e:
                print(f"Warning: Could not load mask image: {e}")
    
    try:
        images, msg = generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_images=num_images,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            seed=seed if seed > 0 else None,
            image=ref_image,
            mask_image=mask_img,
            strength=strength,
        )
        return images, msg
    except Exception as exc:
        import traceback
        return [], f"❌ Generation error: {exc}\n\n{traceback.format_exc()}"


def save_images(
    images: List[Image.Image],
    selected_indices: List[int],
) -> str:
    """Save selected images to disk."""
    if not images:
        return "⚠️ No images to save."
    
    if not selected_indices:
        return "⚠️ No images selected."
    
    saved = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx in selected_indices:
        if 0 <= idx < len(images):
            img = images[idx]
            filename = f"{generator.current_key}_{timestamp}_{idx}.png"
            filepath = OUTPUT_DIR / filename
            img.save(filepath)
            saved.append(filename)
    
    if saved:
        return f"✅ Saved {len(saved)} image(s): {', '.join(saved)}"
    else:
        return "⚠️ No valid images selected."


def select_all_images(images: List[Image.Image]) -> List[int]:
    """Select all images."""
    return list(range(len(images)))


def clear_selection() -> List[int]:
    """Clear image selection."""
    return []


# ------------------------------------------------------------------------- UI
def build_app() -> gr.Blocks:
    """Build and return the Gradio application."""
    with gr.Blocks(title="Local Text-to-Image Generator") as demo:
        gr.Markdown(
            "# 🎨 Local Text-to-Image Generator\n"
            "Generate images from text using open-source models — fully local, no data leaves your machine.\n"
            "Supports **text-to-image**, **image-to-image**, and **inpainting**."
        )

        # Model selection row
        with gr.Row():
            model_dd = gr.Dropdown(
                choices=list(MODEL_REGISTRY.keys()),
                value=DEFAULT_MODEL,
                label="Model",
                scale=3,
            )
            load_btn = gr.Button("🔄 Load model", variant="primary", scale=1)
            unload_btn = gr.Button("🗑️ Unload", scale=1)

        status_md = gr.Markdown("No model loaded.")

        # Model status accordion
        with gr.Accordion("Local weights status", open=False):
            weights_md = gr.Markdown(model_status_markdown())
            refresh_btn = gr.Button("Refresh")

        # Model info accordion
        with gr.Accordion("ℹ️ Model info", open=False):
            info_md = gr.Markdown(get_model_info(DEFAULT_MODEL))

        # Reference image upload (for img2img and inpainting)
        with gr.Accordion("🖼️ Reference Image (optional)", open=False):
            with gr.Row():
                image_upload = gr.Image(
                    label="Reference Image",
                    type="filepath",
                    visible=False,
                )
                mask_upload = gr.Image(
                    label="Mask Image (for inpainting - white=change, black=keep)",
                    type="filepath",
                    visible=False,
                )
            strength_slider = gr.Slider(
                0.0, 1.0, value=0.8, step=0.05,
                label="Strength (how much to change the image)",
                visible=False,
                info="Higher = more change, lower = closer to original"
            )

        # Generation settings
        with gr.Row():
            with gr.Column(scale=2):
                prompt_tb = gr.Textbox(
                    label="Prompt",
                    placeholder="A beautiful sunset over mountains...",
                    lines=3,
                )
                negative_tb = gr.Textbox(
                    label="Negative prompt (what to avoid)",
                    placeholder="blurry, low quality, distorted...",
                    lines=2,
                )
            
            with gr.Column(scale=1):
                num_images_sl = gr.Slider(
                    1, 4, value=1, step=1, label="Number of images"
                )
                seed_num = gr.Number(
                    value=-1, label="Seed (-1 for random)", precision=0
                )

        # Advanced settings accordion
        with gr.Accordion("⚙️ Advanced settings", open=False):
            with gr.Row():
                steps_slider = gr.Slider(
                    1, 150, value=50, step=1, label="Inference steps"
                )
                guidance_slider = gr.Slider(
                    1.0, 20.0, value=7.5, step=0.5, label="Guidance scale"
                )
            with gr.Row():
                width_slider = gr.Slider(
                    256, 2048, value=512, step=64, label="Width"
                )
                height_slider = gr.Slider(
                    256, 2048, value=512, step=64, label="Height"
                )

        # Generate button
        generate_btn = gr.Button("🎨 Generate Images", variant="primary", size="lg")

        # Output gallery
        gallery = gr.Gallery(
            label="Generated Images",
            show_label=True,
            columns=2,
            rows=2,
            height=600,
            object_fit="contain",
        )

        # Image selection and saving
        with gr.Row():
            select_all_btn = gr.Button("☑️ Select All")
            clear_sel_btn = gr.Button("☐ Clear Selection")
            save_btn = gr.Button("💾 Save Selected", variant="primary")

        selected_indices = gr.State([])

        save_status_md = gr.Markdown("")

        # Wire up events
        load_btn.click(
            ui_load_model,
            [model_dd],
            [status_md, weights_md],
        )
        unload_btn.click(
            ui_unload_model,
            None,
            [status_md, weights_md],
        )
        refresh_btn.click(
            lambda: model_status_markdown(),
            None,
            weights_md,
        )

        # Update model info and UI when selection changes
        model_dd.change(
            lambda k: get_model_info(k),
            [model_dd],
            [info_md],
        )
        model_dd.change(
            on_model_change,
            [model_dd],
            [image_upload, mask_upload, strength_slider],
        )

        # Generate images
        generate_btn.click(
            generate_images,
            [
                prompt_tb,
                negative_tb,
                image_upload,
                mask_upload,
                num_images_sl,
                steps_slider,
                guidance_slider,
                width_slider,
                height_slider,
                seed_num,
                strength_slider,
            ],
            [gallery, status_md],
        )

        # Image selection
        gallery.select(
            lambda evt: [evt.index],
            None,
            selected_indices,
        )
        select_all_btn.click(
            select_all_images,
            [gallery],
            selected_indices,
        )
        clear_sel_btn.click(
            clear_selection,
            None,
            selected_indices,
        )

        # Save images
        save_btn.click(
            save_images,
            [gallery, selected_indices],
            save_status_md,
        )

    return demo


if __name__ == "__main__":
    build_app().queue().launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        theme=gr.themes.Soft(),
    )