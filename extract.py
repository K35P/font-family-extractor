#!/usr/bin/env python3
"""Export static fonts for each named instance in a variable font (fvar table)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from fontTools.ttLib import TTLibError, TTFont
from fontTools.varLib import instancer

_INVALID_FS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _sanitize_filename(name: str) -> str:
    cleaned = _INVALID_FS_CHARS.sub("_", name)
    cleaned = cleaned.strip(" .")
    return cleaned or "instance"


def _unique_path(directory: Path, base: str, *, extension: str) -> Path:
    candidate = directory / f"{base}{extension}"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = directory / f"{base}_{n}{extension}"
        if not candidate.exists():
            return candidate
        n += 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract each predefined style from a variable font into static font files."
        )
    )
    parser.add_argument(
        "font_path",
        type=Path,
        help="Path to the variable font file (.ttf or .otf).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Directory where static fonts are written. "
            "Default: a folder next to the input file, named after the font file (without extension)."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    font_path = args.font_path.resolve()

    if not font_path.is_file():
        print(f"Error: file not found: {font_path}", file=sys.stderr)
        return 1

    if args.output_dir is not None:
        out_dir = args.output_dir.resolve()
    else:
        out_dir = font_path.parent / font_path.stem

    suffix = font_path.suffix.lower()
    if suffix not in {".ttf", ".otf"}:
        print(
            "Error: expected a .ttf or .otf variable font file.",
            file=sys.stderr,
        )
        return 1
    out_extension = ".otf" if suffix == ".otf" else ".ttf"

    try:
        with TTFont(font_path) as probe:
            if "fvar" not in probe:
                print(
                    "Error: no 'fvar' table — this file does not appear to be a variable font.",
                    file=sys.stderr,
                )
                return 1
            instances = list(probe["fvar"].instances)
    except TTLibError as exc:
        print(f"Error: could not read font file ({exc}).", file=sys.stderr)
        return 1

    if not instances:
        print(
            "Error: the font has an fvar table but defines no named instances.",
            file=sys.stderr,
        )
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Writing {len(instances)} static font(s) to: {out_dir}")

    for instance in instances:
        name_id = instance.subfamilyNameID
        with TTFont(font_path) as vf:
            label = vf["name"].getDebugName(name_id) or f"instance_{name_id}"
            safe_base = _sanitize_filename(label.replace(" ", "_"))
            dest = _unique_path(out_dir, safe_base, extension=out_extension)
            static_font = instancer.instantiateVariableFont(vf, instance.coordinates)
            static_font.save(dest)
            print(f"  {dest.name}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
