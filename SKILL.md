---
name: comfyui-workflow
description: Generate verified ComfyUI workflow JSON for a GTX 1660 Ti 6GB (SD 1.5 only). Use when the user asks for ComfyUI workflows, txt2img, img2img, inpaint, LoRA, ControlNet, or upscale. Never invent nodes. Copy a templates/6gb file, mutate prompts/seeds only, and run scripts/validate_workflow.py before delivering.
---

# ComfyUI workflows — GTX 1660 Ti 6GB (default)

This fork is locked to **NVIDIA GTX 1660 Ti / 6GB VRAM**.
Hardware cannot run Flux, SDXL @ 1024, or video. Do not emit those graphs.

Upstream node catalog and extra templates remain in this repo for reference only.
**Default generation path is `templates/6gb/` + `scripts/validate_workflow.py`.**

## Hard rules (do not violate)

1. **Never invent a `type` / `class_type`.** If it is not in `references/allowed-nodes.json`, refuse.
2. **Never build a graph from scratch.** Copy one file from `templates/6gb/` and change only:
   - prompts (`CLIPTextEncode` widgets)
   - seed
   - steps (8–30), cfg (1–12), sampler/scheduler from the allowlist
   - checkpoint / LoRA / ControlNet **filenames** (SD 1.5 files only)
   - `filename_prefix`
3. **Do not add, remove, or rewire nodes** unless the user explicitly asks AND the result still passes the validator.
4. **Run** `python3 scripts/validate_workflow.py <file.json>` **before delivering.** If it fails, do not hand the JSON over. Fix from a template and re-run.
5. If the user asks for Flux / SDXL / Wan / Hunyuan / video / 3D / audio: **refuse**, name the 6GB cap, offer the closest SD 1.5 template.
6. One LoRA max. One ControlNet max. Batch size 1. Resolution **≤ 512×512**.
7. Do not chain `ImageUpscaleWithModel` onto a KSampler graph. Upscale is a separate workflow.
8. Prefer **API-safe LiteGraph UI JSON** copied from templates (already valid). Do not guess `widgets_values` order.
9. If you are unsure, say so. Do not fill gaps with invented sockets.

## Profile (always on)

Read `profiles/gtx-1660-ti-6gb.md` and `profiles/gtx-1660-ti-6gb.json`.

| Setting | Value |
|---|---|
| GPU | GTX 1660 Ti, 6GB, Turing, FP16, no BF16 |
| Default graph | `templates/6gb/sd15-txt2img.json` |
| Size | 512×512, batch 1 |
| Steps / CFG | 20 / 7 |
| Sampler | euler_ancestral + karras |
| Launch flags | `--lowvram --use-split-cross-attention --force-fp16` |

## Template picker

Read `templates/6gb/manifest.json`. Pick **one**:

| User intent | File | Tier |
|---|---|---|
| txt2img, "just generate", default | `templates/6gb/sd15-txt2img.json` | 1 start here |
| + one LoRA | `templates/6gb/sd15-lora.json` | 1 |
| img2img | `templates/6gb/sd15-img2img.json` | 1 (input must be 512) |
| inpaint | `templates/6gb/sd15-inpaint.json` | 2 |
| ControlNet (one) | `templates/6gb/sd15-controlnet.json` | 2 |
| upscale only | `templates/6gb/upscale-model.json` | 2 separate run |

Tier 2 only after tier 1 has worked on their machine.

## Allowed nodes

Source of truth: `references/allowed-nodes.json`.

Vanilla ComfyUI only (no custom packs unless the user later adds a verified catalog entry):

CheckpointLoaderSimple, CLIPTextEncode, EmptyLatentImage, KSampler, VAEDecode, VAEEncode, VAEEncodeForInpaint, SaveImage, PreviewImage, LoadImage, LoadImageMask, LoraLoader, ControlNetLoader, ControlNetApplyAdvanced, UpscaleModelLoader, ImageUpscaleWithModel, ImageScale, CLIPSetLastLayer, VAEDecodeTiled, GrowMask, InvertMask.

## Verified widget order (from the templates — do not reorder)

```
CheckpointLoaderSimple: [ckpt_name]
CLIPTextEncode:         [text]
EmptyLatentImage:       [width, height, batch_size]
KSampler:               [seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise]
LoraLoader:             [lora_name, strength_model, strength_clip]
ControlNetLoader:       [control_net_name]
ControlNetApplyAdvanced:[strength, start_percent, end_percent]
LoadImage:              [image]
LoadImageMask:          [image, channel]
VAEEncodeForInpaint:    [grow_mask_by]
SaveImage:              [filename_prefix]
UpscaleModelLoader:     [model_name]
```

`control_after_generate` MUST sit immediately after every seed (`randomize` / `fixed` / `increment` / `decrement`).

## Delivery checklist

- [ ] Copied a `templates/6gb/` JSON, did not author a new graph
- [ ] `python3 scripts/validate_workflow.py <out.json>` exits 0
- [ ] Prompts / seed / filenames are the only intentional edits
- [ ] Model filenames are SD 1.5 (see `references/models-6gb.md`)
- [ ] Told the user which template was used
- [ ] Told them to launch ComfyUI with `--lowvram --use-split-cross-attention --force-fp16`
- [ ] If they asked for a heavy model, refused with the 6GB list in `references/blocked.md`

## Other AIs

Root `SKILL.md` is the contract (Claude Code, Codex, Cursor, Grok).
Grok also loads `.grok/skills/comfyui-workflow/SKILL.md` (pointer to this file).
Do not use `SKILL.upstream.md` for this user's GPU — that file still describes Flux/video.

## Honesty bar

This repo **verifies JSON structure and the node allowlist**. It cannot run a 1660 Ti from chat. After the first local txt2img succeeds, then climb to LoRA / ControlNet.
