# Project Resume & Handover Guide: Auto-script-comfyUI

This document acts as a comprehensive state summary and handover guide for the **Auto-script-comfyUI** project. It outlines the codebase structure, prompt evolution history, current art style, setup instructions, and next steps so that any AI tool or developer can seamlessly resume this project.

---

## 1. Project Context
*   **Project Name / Channel Name:** Stixx Stories (Rebranded from reference "Ink Explainer")
*   **Repository URL:** `git@github.com:gagansharma18/Auto-script-comfyUI.git`
*   **Active Directory:** `C:\Users\gagan\Documents\YOUTUBE\Auto script comfyUI\`
*   **Target Output Vibe:** An educational, high-quality cartoon/webcomic YouTube video style.
*   **Reference Channels:**
    1.  [Ink Explainer](https://www.youtube.com/@Inkexplainer96) (for character simplicity and branding layout)
    2.  [History Alive Animated](https://www.youtube.com/@historyaliveanimated) (for character expressions, hair, clothing, and warm minimalist backgrounds)

---

## 2. Codebase Architecture

The project consists of the following key files:

| File | Purpose | Description |
| :--- | :--- | :--- |
| [`batch_generate.py`](file:///C:/Users/gagan/Documents/YOUTUBE/Auto%20script%20comfyUI/batch_generate.py) | **Python Automation Script** | Automatically reads text scripts line-by-line, parses timestamps, builds prompts using the style template, calls the ComfyUI API, polls for completion, and saves images using a dynamic filename format (`stixx_stories_[sequence_number]_[timestamp]_*.png`). |
| [`image_z_image_turbo.json`](file:///C:/Users/gagan/Documents/YOUTUBE/Auto%20script%20comfyUI/image_z_image_turbo.json) | **Base ComfyUI Workflow** | Single-image API node configuration for the **Z-Image-Turbo** pipeline. |
| [`image_z_image_turbo_batch.json`](file:///C:/Users/gagan/Documents/YOUTUBE/Auto%20script%20comfyUI/image_z_image_turbo_batch.json) | **Batch ComfyUI Workflow** | An in-UI workflow using `LoadText|pysssss` and `StringFunction|pysssss` custom nodes to generate images sequentially inside the ComfyUI interface. |
| [`sample_prompts.txt`](file:///C:/Users/gagan/Documents/YOUTUBE/Auto%20script%20comfyUI/sample_prompts.txt) | **Sample Input File** | Demonstrates the script format (supporting both `00:00 - Description` and plain text descriptions). |
| [`system_prompt.txt`](file:///C:/Users/gagan/Documents/YOUTUBE/Auto%20script%20comfyUI/system_prompt.txt) | **Default Prompt Template** | External text file containing the style instructions structure, passed using `--template`. |

---

## 3. Art Style & Prompt Template Evolution

The visual style for **Stixx Stories** has evolved through three distinct phases:

### Phase 1: Amateur MS Paint
*   **Aesthetic:** Intentionally bad, wobbly thick black outlines, flat colors, completely white backgrounds, centered composition, and dot-eye stick-men with circle heads.
*   **Issue:** Images felt too empty and did not have enough production value for a narrative channel.

### Phase 2: Ink Explainer Inspired
*   **Aesthetic:** Character style retained (simple white circle heads, stick limbs) but rebranded to use the `stixx_stories` filename prefix.

### Phase 3: History Alive Animated + Ink Explainer Blend (Current)
*   **Aesthetic:** Characters are stick figures with large round white circular heads (no skin tone), small dot eyes, thin curved black eyebrows to show emotion, and simple line/oval mouths. They have simplified flat-colored hair blocks with messy spikes, and wear basic flat-colored clothes (such as animal skins, robes, t-shirts, or lab coats).
*   **Backgrounds:** Instead of white space, they are now minimalist, clean settings using a soft, warm color palette (light beige, soft blue, pale green, terracotta). The environment uses simple shapes and soft gradients, sometimes with a subtle depth-of-field blur.
*   **Outlines & Fills:** Thick, slightly irregular wobbly outlines with flat color fills (polished digital webcomic aesthetic with hand-drawn line imperfections).

### The Current Active Prompt Template
The following prompt template is hardcoded as `STYLE_PROMPT_TEMPLATE` in `batch_generate.py`:

```python
STYLE_PROMPT_TEMPLATE = """A horizontal 16:9 widescreen illustration in the style of an animated educational webcomic or YouTube explainer video. The characters are simple stick figures with large round white circular heads, small black dot eyes, thin curved black eyebrows to show emotion, and simple line or oval mouths. Bodies are thin black stick lines with simple line arms and legs. Characters have simplified messy spikes of flat-colored hair (e.g., brown, black, grey) and wear basic, simple flat-colored clothing (such as primitive animal skins, t-shirts, or simple tunics).

The characters and foreground objects have thick, slightly irregular hand-drawn wobbly black outlines. The background is a clean, minimalist illustrated setting with a soft, warm color palette (such as light beige, soft blue, pale green, or terracotta). The background environment is drawn with simple clean shapes, flat coloring, and gentle gradients, occasionally with a very subtle depth-of-field blur.

The overall look is a polished, flat-color digital vector webcomic style with hand-drawn imperfections. There is no complex 3D shading, no realism, and no photo-realistic lighting. Zero written text, zero labels, zero speech bubbles, and zero watermarks.

Scene: {scene_description}"""
```

---

## 4. How to Run the Script

### Pre-requisites
1.  **ComfyUI** running locally at `http://127.0.0.1:8188`.
2.  The following model files installed in your ComfyUI models folders:
    *   `unet_name`: `z_image_turbo_bf16.safetensors`
    *   `clip_name`: `qwen_3_4b.safetensors`
    *   `vae_name`: `ae.safetensors`
3.  Python 3.8+ installed.

### Executing Commands

*   **Dry Run (To preview prompts and filename formatting without running generation):**
    ```bash
    # On Windows PowerShell:
    $env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt --dry-run
    ```

*   **Run Generation:**
    ```bash
    $env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt
    ```

*   **Custom Server & Settings:**
    ```bash
    $env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt --server http://127.0.0.1:8188 --steps 8 --width 1280 --height 720
    ```

*   **With Custom Style Prompt Template:**
    ```bash
    $env:PYTHONIOENCODING='utf-8'; python batch_generate.py --input sample_prompts.txt --template system_prompt.txt
    ```

---

## 5. Next Steps Checklist

When you resume with a new AI model or start another session, you should focus on:

- [ ] **Run a test generation:** Ensure ComfyUI is up, run the python script on `sample_prompts.txt`, and check the generated images in your ComfyUI output directory.
- [ ] **Aesthetic Verification:** Check if the generated characters match the expected visual profile (large white heads, dot eyes, stick body, warm clean backgrounds). Adjust details in `STYLE_PROMPT_TEMPLATE` if the lines are too thin, backgrounds too detailed, or if the model starts rendering realistic faces/skin tones.
- [ ] **Workflow Fine-tuning:** If the model generation is slow, adjust `--steps` or verify that ComfyUI uses Z-Image-Turbo.
