#!/usr/bin/env python3
"""Unit tests: 6GB templates pass; banned graphs fail."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_workflow import load_json, validate, CATALOG_PATH, PROFILE_PATH  # noqa: E402

catalog = load_json(CATALOG_PATH)
profile = load_json(PROFILE_PATH)


def assert_ok(data, label):
    errs = validate(data, catalog, profile)
    if errs:
        raise SystemExit(f"expected PASS for {label}: {errs}")
    print(f"PASS  {label}")


def assert_fail(data, label, must_contain=None):
    errs = validate(data, catalog, profile)
    if not errs:
        raise SystemExit(f"expected FAIL for {label}")
    blob = " | ".join(errs)
    if must_contain and must_contain not in blob:
        raise SystemExit(f"{label} failed for the wrong reason: {blob}")
    print(f"PASS  {label} correctly rejected ({blob.split(' | ')[0]})")


def main() -> int:
    templates = sorted((ROOT / "templates" / "6gb").glob("sd15-*.json")) + [
        ROOT / "templates" / "6gb" / "upscale-model.json"
    ]
    if len(templates) != 6:
        raise SystemExit(f"expected 6 templates, found {templates}")

    for path in templates:
        data = load_json(path)
        assert_ok(data, path.name)
        # prompt mutation must still pass
        mutated = copy.deepcopy(data)
        for node in mutated["nodes"]:
            if node["type"] == "CLIPTextEncode" and node.get("widgets_values"):
                node["widgets_values"][0] = "a red fox in snow, masterpiece"
        assert_ok(mutated, f"{path.name} prompt-mutated")

    txt = load_json(ROOT / "templates" / "6gb" / "sd15-txt2img.json")

    flux = copy.deepcopy(txt)
    flux["nodes"][0]["type"] = "UNETLoader"
    assert_fail(flux, "invented UNETLoader", "not in the 6GB allowlist")

    big = copy.deepcopy(txt)
    for node in big["nodes"]:
        if node["type"] == "EmptyLatentImage":
            node["widgets_values"] = [1024, 1024, 1]
    assert_fail(big, "1024 latent", "exceeds 6GB max")

    batch = copy.deepcopy(txt)
    for node in batch["nodes"]:
        if node["type"] == "EmptyLatentImage":
            node["widgets_values"] = [512, 512, 4]
    assert_fail(batch, "batch 4", "batch_size")

    ckpt = copy.deepcopy(txt)
    for node in ckpt["nodes"]:
        if node["type"] == "CheckpointLoaderSimple":
            node["widgets_values"] = ["sd_xl_base_1.0.safetensors"]
    assert_fail(ckpt, "sdxl checkpoint", "not a 6GB SD1.5")

    print("OK  all tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
