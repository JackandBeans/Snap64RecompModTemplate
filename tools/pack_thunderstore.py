"""The mod's Thunderstore package: dist/<team>-<Name>-<version>.zip, holding
manifest.json (made from mod.toml), README.md, CHANGELOG.md and icon.png
from thunderstore/, and the built .nrm, all at the zip's root. That is the
layout Thunderstore's upload page checks, and the one Snap64 Recomp 1.1.0
unpacks when the zip is dropped on its window or left in its mods folder.

    python tools/pack_thunderstore.py --team YourTeam [--website URL]

The team is the Thunderstore team you upload as. The package's name is the
mod's display_name with spaces as underscores, its description the
short_description (Thunderstore takes 250 characters), its version the
mod's version. Needs Python 3.11 (tomllib); nothing else.
"""
import argparse
import json
import os
import re
import struct
import sys
import tomllib
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fail(message):
    sys.exit("pack_thunderstore: " + message)


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        fail(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", required=True)
    parser.add_argument("--website", default="")
    parser.add_argument("--build", default="build")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()

    with open(os.path.join(ROOT, "mod.toml"), "rb") as f:
        spec = tomllib.load(f)
    manifest = spec["manifest"]
    name = re.sub(r"[^A-Za-z0-9_]", "", manifest["display_name"].replace(" ", "_"))
    version = manifest["version"]
    description = manifest["short_description"]
    if not re.fullmatch(r"[A-Za-z0-9_]+", args.team):
        fail(f"the team {args.team!r} may use only letters, digits and underscores")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"version {version!r} is not major.minor.patch")
    if len(description) > 250:
        fail(f"the short description is {len(description)} characters; Thunderstore takes 250")

    here = os.path.join(ROOT, "thunderstore")
    icon = os.path.join(here, "icon.png")
    if png_size(icon) != (256, 256):
        fail(f"{icon} is {png_size(icon)}; Thunderstore wants 256x256")
    nrm = os.path.join(ROOT, args.build, spec["inputs"]["mod_filename"] + ".nrm")
    if not os.path.isfile(nrm):
        fail(f"{nrm} is missing; build the mod first (make, then RecompModTool mod.toml build)")

    ts_manifest = {
        "name": name,
        "version_number": version,
        "website_url": args.website,
        "description": description,
        "dependencies": [],
    }
    os.makedirs(os.path.join(ROOT, args.out), exist_ok=True)
    zip_path = os.path.join(ROOT, args.out, f"{args.team}-{name}-{version}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(ts_manifest, indent=4, ensure_ascii=False) + "\n")
        for extra in ("README.md", "CHANGELOG.md", "icon.png"):
            path = os.path.join(here, extra)
            if os.path.isfile(path):
                z.write(path, extra)
            elif extra != "CHANGELOG.md":
                fail(f"{path} is missing")
        z.write(nrm, os.path.basename(nrm))
    print(f"{os.path.relpath(zip_path, ROOT)}: {name} {version}, {os.path.getsize(zip_path)} bytes")


if __name__ == "__main__":
    main()
