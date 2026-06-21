# Auto-script-comfyUI 🎨🎥

An automation pipeline that reads text scripts line-by-line (with or without timestamps), formats them into custom style prompts, and batches image generation directly through the **ComfyUI API** (using the **Z-Image-Turbo** model workflow).

This tool is designed to automate asset generation for narrative YouTube channels, educational explainer videos, and cartoon webcomics.

---

## 🚀 Key Features

*   **Script Parser**: Supports both timestamped lines (e.g. `01:24 - Prehistoric hunter looking at a pelt`) and plain-text descriptions.
*   **Custom Style Templates**: Load external style guidelines (`--template`) to keep visual continuity across episodes.
*   **API Automation**: Queues generations, waits for completions, generates unique filenames based on line numbers/timestamps, and saves outputs.
*   **No Third-Party Python Dependencies**: Runs on standard Python libraries.

---

## 🛠️ Prerequisites & Setup

### 1. Python
Requires **Python 3.8+** installed on your system.

### 2. ComfyUI Configuration
Make sure you have ComfyUI running locally (usually at `http://127.0.0.1:8188`). The workflow is configured to use the **Z-Image-Turbo** pipeline.

Required model files inside ComfyUI directories:
*   **UNET**: `z_image_turbo_bf16.safetensors`
*   **CLIP**: `qwen_3_4b.safetensors`
*   **VAE**: `ae.safetensors`

---

## 📖 How to Run the Script

Always run the python command setting the UTF-8 encoding environment variable on Windows to prevent parsing errors.

### 1. Dry Run (Preview Prompts & Filename Formatting)
Prints compiled prompts to the console without sending requests to ComfyUI:
```powershell
$env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt --dry-run
```

### 2. Run Image Generation
```powershell
$env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt
```

### 3. Pass a Custom Style Template / System Prompt File
```powershell
$env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt --template system_prompt.txt
```

### 4. Custom Server, Steps, and Resolution
```powershell
$env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt --server http://127.0.0.1:8188 --steps 8 --width 1280 --height 720
```

---

## 🗂️ CLI Arguments Reference

| Argument | Short Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | *Required* | Path to the text script file with one description per line. |
| `--template` | `-T` | `None` | Path to a text file containing the style prompt template. |
| `--server` | `-s` | `http://127.0.0.1:8188` | ComfyUI server address URL. |
| `--prefix` | `-p` | `stixx_stories` | Prefix used for saved filenames. |
| `--width` | `-W` | `1280` | Width of generated images (16:9 widescreen default). |
| `--height` | `-H` | `720` | Height of generated images (16:9 widescreen default). |
| `--steps` | | `8` | Number of sampling steps in KSampler. |
| `--timeout` | `-t` | `300` | Max seconds to wait for generation per image. |
| `--dry-run` | | | If passed, prints logs of compile prompts without generating. |

---

## 📁 File Structure

*   [`batch_generate.py`](batch_generate.py): The main automation script.
*   [`system_prompt.txt`](system_prompt.txt): The external template file containing the default explainer style.
*   [`sample_prompts.txt`](sample_prompts.txt): A short sample input file demonstrating timestamp script format.
*   [`image_z_image_turbo.json`](image_z_image_turbo.json): Base ComfyUI workflow (API node format) loaded by the script.
*   [`project_resume_guide.md`](project_resume_guide.md): Comprehensive handover and resume guide documenting the visual history and development guidelines.
