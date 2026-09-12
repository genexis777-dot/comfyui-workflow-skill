# ComfyUI workflow skill — GTX 1660 Ti 6GB

Fork of [LingyiChen-AI/comfyui-workflow-skill](https://github.com/LingyiChen-AI/comfyui-workflow-skill) locked to a **6GB GTX 1660 Ti**.

Natural language → ComfyUI JSON, but **only** graphs that can actually load on this card.

- Default: **SD 1.5 @ 512×512**, batch 1
- Agents **copy** `templates/6gb/`, they do not invent nodes
- `scripts/validate_workflow.py` must pass before a workflow is delivered
- Flux / SDXL / video templates from upstream are **not** used unless you change hardware

Works with Grok, Claude Code, Cursor, Codex, or any agent that reads `SKILL.md`.

## What is allowed

| Template | Use |
|---|---|
| `templates/6gb/sd15-txt2img.json` | Start here |
| `templates/6gb/sd15-lora.json` | One LoRA |
| `templates/6gb/sd15-img2img.json` | img2img (512 input) |
| `templates/6gb/sd15-inpaint.json` | Inpaint |
| `templates/6gb/sd15-controlnet.json` | One ControlNet |
| `templates/6gb/upscale-model.json` | Upscale only, separate run |

## What is blocked

Flux, SDXL 1024, Wan, Hunyuan, LTXV, Mochi, Cosmos, 3D, audio. Details: `references/blocked.md`.

## For agents

1. Read `SKILL.md`
2. Pick one file in `templates/6gb/`
3. Change prompts / seed / filenames only
4. Run `python3 scripts/validate_workflow.py path/to/out.json`
5. Deliver only if it prints `OK`

## For you (when you are back at the laptop)

```text
git clone https://github.com/genexis777-dot/comfyui-workflow-skill.git
python3 comfyui-workflow-skill/scripts/test_templates.py
```

Launch ComfyUI:

```text
--lowvram --use-split-cross-attention --force-fp16
```

First run: drag `templates/6gb/sd15-txt2img.json` onto ComfyUI.
Put `v1-5-pruned-emaonly.safetensors` in `models/checkpoints/`.

## Verify locally

```text
python3 scripts/validate_workflow.py --all-6gb
python3 scripts/test_templates.py
```

These tests check JSON + the allowlist. They do **not** execute the GPU. After txt2img works on the 1660 Ti, try LoRA, then ControlNet.

## Other AIs

Clone or connect this same repo. Root `SKILL.md` is the contract. Grok also sees `.grok/skills/comfyui-workflow/`.

## Credits

- Upstream skill, node catalog, SD 1.5 templates: [LingyiChen-AI/comfyui-workflow-skill](https://github.com/LingyiChen-AI/comfyui-workflow-skill) (MIT)
- ComfyUI: [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
