# Profile: GTX 1660 Ti 6GB

Machine this repo is built for.

- GPU: NVIDIA GeForce GTX 1660 Ti
- VRAM: 6 GB
- Arch: Turing — FP16 yes, BF16 no, no Tensor cores
- Goal: graphs that load without fighting the card

## Will run (tier 1)

- SD 1.5 txt2img 512×512, batch 1, ~20 steps
- Same + one LoRA
- img2img at 512 (resize the photo first)

## Try next (tier 2)

- One SD 1.5 ControlNet at 512 (`--lowvram` if tight)
- SD 1.5 inpaint at 512
- ESRGAN upscale as a **separate** workflow after unload

## Will not run (do not generate)

Flux, SDXL 1024, SD3, Wan, Hunyuan, LTXV, Mochi, Cosmos, SVD, AnimateDiff, IP-Adapter piles, two ControlNets, refiners, video, 3D, audio.

See `references/blocked.md`.

## ComfyUI launch

```
--lowvram --use-split-cross-attention --force-fp16
```

Add `--cpu-vae` only if VAE decode still OOMs (slow).

## Models that fit

Pruned SD 1.5 checkpoints (~2 GB), one SD 1.5 LoRA, one SD 1.5 ControlNet. Filenames: `references/models-6gb.md`.
