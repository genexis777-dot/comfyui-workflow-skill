---
name: comfyui-workflow
description: Generate verified ComfyUI workflow JSON for GTX 1660 Ti 6GB. Always read the repository root SKILL.md. Copy templates/6gb, never invent nodes, run scripts/validate_workflow.py.
---

# Grok entry

This skill lives at the **repository root**, not only in this folder.

Required reads (in order):

1. `SKILL.md` (root) — hard rules
2. `profiles/gtx-1660-ti-6gb.md` — hardware cap
3. `templates/6gb/manifest.json` — the only graphs you may emit
4. `references/allowed-nodes.json` — the only node types you may use

Then copy one `templates/6gb/*.json`, mutate prompts/seeds/filenames, and run:

```
python3 scripts/validate_workflow.py path/to/workflow.json
```

Refuse Flux / SDXL / video. Default is SD 1.5 512×512.
