# Models that belong on this card

Use these filenames in widgets. Prefer Hugging Face official SD 1.5 files.

## Checkpoint (models/checkpoints/)

| File | Notes |
|---|---|
| `v1-5-pruned-emaonly.safetensors` | Default. ~4 GB pruned SD 1.5. |
| `sd-v1-5-inpainting.ckpt` | Inpaint template only. |

Any other **SD 1.5** community checkpoint (~2 GB pruned) is OK if the user names the exact file they already have. Never substitute an SDXL/Flux file.

Download (official):
https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors

## LoRA (models/loras/)

User-supplied SD 1.5 LoRA only. Keep the placeholder `example_lora.safetensors` until they give a real filename. Strength 0.6–1.0.

## ControlNet (models/controlnet/)

SD 1.5 ControlNet 1.1, one at a time:

- `control_v11p_sd15_canny.safetensors`
- `control_v11p_sd15_openpose.safetensors`
- `control_v11f1p_sd15_depth.safetensors`

https://huggingface.co/comfyanonymous/control_v11p_sd15_canny

## Upscale (models/upscale_models/)

- Prefer 2x if 4x OOMs
- Template default: `RealESRGAN_x4plus.pth` (run **without** SD loaded)

## Do not list as defaults

Anything with `xl`, `flux`, `sd3`, `wan`, `hunyuan`, `gguf` Flux, or `bf16` video weights.
