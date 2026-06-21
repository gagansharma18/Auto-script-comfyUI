"""
ComfyUI Batch Image Generator from Text File
=============================================
This script reads a text file (with timestamped lines), and for each line:
1. Wraps it in the MS Paint style prompt template
2. Sends it to ComfyUI via the API
3. Waits for the image to be generated before moving to the next line

USAGE:
    python batch_generate.py --input prompts.txt
    python batch_generate.py --input prompts.txt --server http://127.0.0.1:8188

TEXT FILE FORMAT (each line = one image):
    00:00 - Early humans on the African savanna
    00:05 - A caveman discovering fire
    00:10 - Two stick figures trading goods

    OR simply (no timestamps):
    Early humans on the African savanna
    A caveman discovering fire
    Two stick figures trading goods

REQUIREMENTS:
    - ComfyUI running locally (default: http://127.0.0.1:8188)
    - Z-Image-Turbo model files installed in ComfyUI
    - Python 3.8+
"""

import json
import urllib.request
import urllib.error
import argparse
import time
import re
import uuid
import os
import sys

# ─────────────────────────────────────────────────────────────
# STYLE PROFILE PROMPT TEMPLATE
# ─────────────────────────────────────────────────────────────
STYLE_PROMPT_TEMPLATE = """A horizontal 16:9 widescreen illustration in the style of an animated educational webcomic or YouTube explainer video. The characters are simple stick figures with large round white circular heads, small black dot eyes, thin curved black eyebrows to show emotion, and simple line or oval mouths. Bodies are thin black stick lines with simple line arms and legs. Characters have simplified messy spikes of flat-colored hair (e.g., brown, black, grey) and wear basic, simple flat-colored clothing (such as primitive animal skins, t-shirts, or simple tunics).

The characters and foreground objects have thick, slightly irregular hand-drawn wobbly black outlines. The background is a clean, minimalist illustrated setting with a soft, warm color palette (such as light beige, soft blue, pale green, or terracotta). The background environment is drawn with simple clean shapes, flat coloring, and gentle gradients, occasionally with a very subtle depth-of-field blur.

The overall look is a polished, flat-color digital vector webcomic style with hand-drawn imperfections. There is no complex 3D shading, no realism, and no photo-realistic lighting. Zero written text, zero labels, zero speech bubbles, and zero watermarks.

Scene: {scene_description}"""

# ─────────────────────────────────────────────────────────────
# COMFYUI API WORKFLOW (API FORMAT)
# This is the Z-Image-Turbo pipeline in API-node format
# ─────────────────────────────────────────────────────────────
WORKFLOW_API = {
    "28": {
        "class_type": "UNETLoader",
        "inputs": {
            "unet_name": "z_image_turbo_bf16.safetensors",
            "weight_dtype": "default"
        }
    },
    "30": {
        "class_type": "CLIPLoader",
        "inputs": {
            "clip_name": "qwen_3_4b.safetensors",
            "type": "lumina2",
            "device": "default"
        }
    },
    "29": {
        "class_type": "VAELoader",
        "inputs": {
            "vae_name": "ae.safetensors"
        }
    },
    "27": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "__PROMPT_PLACEHOLDER__",
            "clip": ["30", 0]
        }
    },
    "33": {
        "class_type": "ConditioningZeroOut",
        "inputs": {
            "conditioning": ["27", 0]
        }
    },
    "13": {
        "class_type": "EmptySD3LatentImage",
        "inputs": {
            "width": 1280,
            "height": 720,
            "batch_size": 1
        }
    },
    "11": {
        "class_type": "ModelSamplingAuraFlow",
        "inputs": {
            "shift": 3,
            "model": ["28", 0]
        }
    },
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 0,
            "control_after_generate": "randomize",
            "steps": 8,
            "cfg": 1,
            "sampler_name": "res_multistep",
            "scheduler": "simple",
            "denoise": 1,
            "model": ["11", 0],
            "positive": ["27", 0],
            "negative": ["33", 0],
            "latent_image": ["13", 0]
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["3", 0],
            "vae": ["29", 0]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "stixx_stories",
            "images": ["8", 0]
        }
    }
}


def parse_line(line: str) -> tuple[str, str]:
    """
    Parse a line from the text file.
    Supports formats:
        00:00 - Description text
        00:00:00 - Description text
        [00:00] Description text
        Just plain description text

    Returns (timestamp_or_index, scene_description)
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None, None

    # Pattern: 00:00 - text  OR  00:00:00 - text
    match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(.+)$', line)
    if match:
        return match.group(1), match.group(2).strip()

    # Pattern: [00:00] text
    match = re.match(r'^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.+)$', line)
    if match:
        return match.group(1), match.group(2).strip()

    # Plain text (no timestamp)
    return None, line


def build_prompt(scene_description: str, style_template: str = STYLE_PROMPT_TEMPLATE) -> str:
    """Build the full styled prompt from a scene description."""
    return style_template.format(scene_description=scene_description)


def get_history(server: str, prompt_id: str) -> dict:
    """Poll ComfyUI for the history of a completed prompt."""
    url = f"{server}/history/{prompt_id}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
    except urllib.error.URLError:
        return {}


def queue_prompt(server: str, workflow: dict, client_id: str) -> str:
    """Send a prompt to ComfyUI and return the prompt_id."""
    payload = json.dumps({
        "prompt": workflow,
        "client_id": client_id
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{server}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        return result.get("prompt_id")


def wait_for_completion(server: str, prompt_id: str, timeout: int = 300) -> bool:
    """Wait for a prompt to finish generating."""
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(server, prompt_id)
        if prompt_id in history:
            status = history[prompt_id].get("status", {})
            if status.get("completed", False) or status.get("status_str") == "success":
                return True
            # Check for outputs as a sign of completion
            outputs = history[prompt_id].get("outputs", {})
            if outputs:
                return True
        time.sleep(1.5)
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Batch generate MS Paint style images from a text file using ComfyUI + Z-Image-Turbo"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the text file with one scene description per line"
    )
    parser.add_argument(
        "--server", "-s",
        default="http://127.0.0.1:8188",
        help="ComfyUI server URL (default: http://127.0.0.1:8188)"
    )
    parser.add_argument(
        "--prefix", "-p",
        default="stixx_stories",
        help="Filename prefix for saved images (default: stixx_stories)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=300,
        help="Max seconds to wait per image (default: 300)"
    )
    parser.add_argument(
        "--width", "-W",
        type=int,
        default=1280,
        help="Image width (default: 1280 for 16:9)"
    )
    parser.add_argument(
        "--height", "-H",
        type=int,
        default=720,
        help="Image height (default: 720 for 16:9)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=8,
        help="Sampling steps (default: 8)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without sending to ComfyUI"
    )
    parser.add_argument(
        "--template", "-T",
        help="Path to a text file containing the style prompt template (uses STYLE_PROMPT_TEMPLATE by default)"
    )

    args = parser.parse_args()

    # ── Read prompt template ─────────────────────────────────
    style_template = STYLE_PROMPT_TEMPLATE
    if args.template:
        if not os.path.exists(args.template):
            print(f"❌ Template file not found: {args.template}")
            sys.exit(1)
        with open(args.template, "r", encoding="utf-8") as f:
            style_template = f.read()

    # ── Read input file ──────────────────────────────────────
    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # ── Parse lines ──────────────────────────────────────────
    scenes = []
    for idx, raw_line in enumerate(raw_lines, start=1):
        ts, desc = parse_line(raw_line)
        if desc is None:
            continue
        label = ts if ts else f"line_{idx:04d}"
        scenes.append((label, desc))

    if not scenes:
        print("❌ No valid lines found in the input file.")
        sys.exit(1)

    print(f"📄 Found {len(scenes)} scene(s) to generate.\n")
    print("=" * 60)

    # ── Generate images ──────────────────────────────────────
    client_id = str(uuid.uuid4())

    for i, (label, scene_desc) in enumerate(scenes, start=1):
        full_prompt = build_prompt(scene_desc, style_template)

        # Sanitize label for filename
        safe_label = re.sub(r'[^\w\-]', '_', label)
        filename_prefix = f"{args.prefix}_{i:04d}_{safe_label}"

        print(f"\n🎨 [{i}/{len(scenes)}]  Timestamp: {label}")
        print(f"   Scene: {scene_desc}")
        print(f"   File:  {filename_prefix}_*.png")

        if args.dry_run:
            print(f"   Prompt:\n{full_prompt[:200]}...")
            continue

        # Build workflow for this scene
        workflow = json.loads(json.dumps(WORKFLOW_API))  # deep copy
        workflow["27"]["inputs"]["text"] = full_prompt
        workflow["13"]["inputs"]["width"] = args.width
        workflow["13"]["inputs"]["height"] = args.height
        workflow["3"]["inputs"]["steps"] = args.steps
        workflow["3"]["inputs"]["seed"] = int(time.time() * 1000) % (2**53)
        workflow["9"]["inputs"]["filename_prefix"] = filename_prefix

        try:
            prompt_id = queue_prompt(args.server, workflow, client_id)
            print(f"   ⏳ Queued (ID: {prompt_id[:8]}...)  Waiting...")

            success = wait_for_completion(args.server, prompt_id, args.timeout)
            if success:
                print(f"   ✅ Done!")
            else:
                print(f"   ⚠️  Timed out after {args.timeout}s — moving to next.")

        except urllib.error.URLError as e:
            print(f"   ❌ Connection error: {e}")
            print(f"   Make sure ComfyUI is running at {args.server}")
            sys.exit(1)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    print("\n" + "=" * 60)
    print(f"🏁 Batch complete! Generated {len(scenes)} image(s).")
    print(f"   Images saved in ComfyUI output directory with prefix: {args.prefix}_*")


if __name__ == "__main__":
    main()
