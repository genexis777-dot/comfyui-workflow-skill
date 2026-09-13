#!/usr/bin/env python3
"""Validate ComfyUI LiteGraph JSON for the gtx-1660-ti-6gb profile.

Fail closed: unknown nodes, illegal sizes, and broken links are errors.
Does not run ComfyUI or a GPU. Structural + catalog checks only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references" / "allowed-nodes.json"
PROFILE_PATH = ROOT / "profiles" / "gtx-1660-ti-6gb.json"
MANIFEST_PATH = ROOT / "templates" / "6gb" / "manifest.json"

REQUIRED_TOP = (
    "id",
    "last_node_id",
    "last_link_id",
    "nodes",
    "links",
    "version",
)

KSampler_WIDGETS = {
    "seed": 0,
    "control_after_generate": 1,
    "steps": 2,
    "cfg": 3,
    "sampler_name": 4,
    "scheduler": 5,
    "denoise": 6,
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def validate(workflow: dict, catalog: dict, profile: dict) -> list[str]:
    errors: list[str] = []
    nodes_spec = catalog["nodes"]
    banned = catalog["banned_type_substrings"]
    limits = profile["limits"]
    allowed_samplers = set(catalog["samplers"])
    allowed_schedulers = set(catalog["schedulers"])

    for key in REQUIRED_TOP:
        if key not in workflow:
            fail(errors, f"missing top-level key: {key}")
    if errors:
        return errors

    if not isinstance(workflow["nodes"], list) or not workflow["nodes"]:
        fail(errors, "nodes must be a non-empty array")
        return errors
    if not isinstance(workflow["links"], list):
        fail(errors, "links must be an array")
        return errors

    nodes = {}
    for node in workflow["nodes"]:
        if "id" not in node or "type" not in node:
            fail(errors, f"node missing id/type: {node}")
            continue
        nid = node["id"]
        if nid in nodes:
            fail(errors, f"duplicate node id {nid}")
        nodes[nid] = node

        ntype = node["type"]
        for bit in banned:
            if bit in ntype:
                fail(errors, f"node {nid} type {ntype!r} is banned on 6GB ({bit})")
        if ntype not in nodes_spec:
            fail(errors, f"node {nid} type {ntype!r} is not in the 6GB allowlist")
            continue

        spec = nodes_spec[ntype]
        widgets = node.get("widgets_values")
        if spec["widget_count"] == 0:
            if widgets not in (None, []):
                fail(errors, f"node {nid} ({ntype}) should have no widgets_values, got {widgets!r}")
        else:
            if not isinstance(widgets, list):
                fail(errors, f"node {nid} ({ntype}) missing widgets_values list")
            elif len(widgets) < spec["widget_count"]:
                fail(
                    errors,
                    f"node {nid} ({ntype}) widgets_values length {len(widgets)} < {spec['widget_count']}",
                )

        if ntype == "KSampler" and isinstance(widgets, list) and len(widgets) >= 7:
            if widgets[1] not in ("randomize", "fixed", "increment", "decrement"):
                fail(errors, f"KSampler {nid} missing control_after_generate after seed")
            steps = widgets[2]
            cfg = widgets[3]
            sampler = widgets[4]
            scheduler = widgets[5]
            denoise = widgets[6]
            if not isinstance(steps, int) or not (limits["steps_min"] <= steps <= limits["steps_max"]):
                fail(errors, f"KSampler {nid} steps {steps} outside {limits['steps_min']}-{limits['steps_max']}")
            if not isinstance(cfg, (int, float)) or not (limits["cfg_min"] <= float(cfg) <= limits["cfg_max"]):
                fail(errors, f"KSampler {nid} cfg {cfg} outside {limits['cfg_min']}-{limits['cfg_max']}")
            if sampler not in allowed_samplers:
                fail(errors, f"KSampler {nid} unknown sampler {sampler!r}")
            if scheduler not in allowed_schedulers:
                fail(errors, f"KSampler {nid} unknown scheduler {scheduler!r}")
            if not isinstance(denoise, (int, float)) or not (0 <= float(denoise) <= 1):
                fail(errors, f"KSampler {nid} denoise {denoise} not in 0-1")

        if ntype == "EmptyLatentImage" and isinstance(widgets, list) and len(widgets) >= 3:
            w, h, b = widgets[0], widgets[1], widgets[2]
            for label, val in (("width", w), ("height", h)):
                if not isinstance(val, int) or val % limits["size_multiple"] != 0:
                    fail(errors, f"EmptyLatentImage {nid} {label}={val} must be multiple of {limits['size_multiple']}")
                if isinstance(val, int) and val > limits[f"max_{label}"]:
                    fail(errors, f"EmptyLatentImage {nid} {label}={val} exceeds 6GB max {limits[f'max_{label}']}")
            if b != limits["batch_size"]:
                fail(errors, f"EmptyLatentImage {nid} batch_size={b} must be {limits['batch_size']}")

        ckpt = None
        if ntype == "CheckpointLoaderSimple" and isinstance(widgets, list) and widgets:
            ckpt = str(widgets[0]).lower()
        if ckpt:
            for bad in ("xl", "flux", "sd3", "hunyuan", "wan", "turbo-xl"):
                if bad in ckpt and not (bad == "xl" and "sdxl" not in ckpt and "xl" not in ckpt):
                    pass
            if any(k in ckpt for k in ("sdxl", "sd_xl", "xl_base", "xl_refiner", "flux", "sd3", "hunyuan", "wan2", "ponyxl")):
                fail(errors, f"CheckpointLoaderSimple {nid} model {widgets[0]!r} is not a 6GB SD1.5 checkpoint")

    types = [n["type"] for n in nodes.values()]
    if types.count("LoraLoader") > limits["max_loras"]:
        fail(errors, f"too many LoraLoader nodes ({types.count('LoraLoader')})")
    if types.count("ControlNetLoader") > limits["max_controlnets"]:
        fail(errors, f"too many ControlNetLoader nodes ({types.count('ControlNetLoader')})")
    if types.count("KSampler") > limits["max_ksamplers"]:
        fail(errors, f"too many KSampler nodes ({types.count('KSampler')})")
    if not any(t in ("SaveImage", "PreviewImage") for t in types):
        fail(errors, "workflow needs SaveImage or PreviewImage")

    # Upscale + KSampler together is the usual 6GB OOM
    if "KSampler" in types and "ImageUpscaleWithModel" in types:
        fail(errors, "do not chain upscale model with KSampler on 6GB; use templates/6gb/upscale-model.json separately")

    by_id = nodes
    for i, link in enumerate(workflow["links"]):
        if not (isinstance(link, list) and len(link) >= 6):
            fail(errors, f"link {i} is not [id, src, src_slot, tgt, tgt_slot, type]")
            continue
        _, src, src_slot, tgt, tgt_slot, ltype = link[:6]
        if src not in by_id:
            fail(errors, f"link {link[0]} source node {src} missing")
            continue
        if tgt not in by_id:
            fail(errors, f"link {link[0]} target node {tgt} missing")
            continue
        src_type = by_id[src]["type"]
        tgt_type = by_id[tgt]["type"]
        if src_type not in nodes_spec or tgt_type not in nodes_spec:
            continue
        src_outs = nodes_spec[src_type]["outputs"]
        if not isinstance(src_slot, int) or src_slot < 0 or src_slot >= len(src_outs):
            fail(errors, f"link {link[0]} src slot {src_slot} invalid for {src_type}")
        else:
            expected = src_outs[src_slot]
            if ltype != expected:
                fail(
                    errors,
                    f"link {link[0]} type {ltype!r} != {src_type} slot {src_slot} ({expected})",
                )

    # every connection input on required nodes should have a link
    for nid, node in by_id.items():
        spec = nodes_spec.get(node["type"])
        if not spec:
            continue
        inputs = {inp.get("name"): inp for inp in node.get("inputs") or [] if isinstance(inp, dict)}
        for cname in spec.get("connection_inputs", {}):
            if cname not in inputs:
                # some templates omit the inputs[] metadata and only use links
                continue
            if inputs[cname].get("link") in (None,):
                fail(errors, f"node {nid} ({node['type']}) connection {cname} is not linked")

    return errors


def validate_path(path: Path, catalog: dict, profile: dict) -> list[str]:
    try:
        data = load_json(path)
    except json.JSONDecodeError as e:
        return [f"{path}: invalid JSON ({e})"]
    errs = validate(data, catalog, profile)
    return [f"{path.name}: {e}" for e in errs]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="workflow JSON files")
    parser.add_argument("--all-6gb", action="store_true", help="validate templates/6gb/*.json")
    args = parser.parse_args(argv)

    catalog = load_json(CATALOG_PATH)
    profile = load_json(PROFILE_PATH)

    paths: list[Path] = list(args.paths)
    if args.all_6gb or not paths:
        paths.extend(sorted((ROOT / "templates" / "6gb").glob("*.json")))
        paths = [p for p in paths if p.name != "manifest.json"]

    if not paths:
        print("no files to validate", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for path in paths:
        errs = validate_path(path, catalog, profile)
        if errs:
            all_errors.extend(errs)
        else:
            print(f"PASS  {path}")

    if all_errors:
        print("FAIL")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print(f"OK  {len(paths)} workflow(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
