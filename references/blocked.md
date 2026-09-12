# Blocked on GTX 1660 Ti 6GB

Do not emit workflows that use these families. The upstream `templates/` folder still contains them for other GPUs — ignore them unless the user explicitly changes hardware profile.

| Family | Why |
|---|---|
| Flux Dev / Schnell (full) | 8–24 GB class, BF16-oriented |
| SDXL @ 1024 | Typically OOM at 6 GB |
| SD3 | Triple CLIP + large UNET |
| Wan / Hunyuan / LTXV / Mochi / Cosmos | Video, far above 6 GB |
| Stable Cascade, Hunyuan3D, Stable Audio | Wrong size / extra models |
| IP-Adapter + ControlNet stacks | Peak VRAM |
| AnimateDiff / SVD | Video |
| Multiple LoRAs or ControlNets | Extra tensors |

If asked, reply with the closest `templates/6gb/` file instead of a heavy graph.
