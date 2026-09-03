"""
Fig Spec Importer & Converter.
Fetches and converts completion specs from withfig/autocomplete (or local files)
directly into Kapsel-compliant Fig.Spec JSON format.
"""

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Optional
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT_DIR / "kapsel" / "core" / "completion" / "specs"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/withfig/autocomplete/master/src"


def fetch_remote_ts_spec(tool_name: str) -> Optional[str]:
    url = f"{GITHUB_RAW_BASE}/{tool_name}.ts"
    print(f"🌐 Fetching Fig spec from: {url}")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Kapsel/0.2.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8")
    except Exception as e:
        print(f"⚠️ Could not fetch remote spec for '{tool_name}': {e}")
    return None


def parse_simple_ts_to_dict(tool_name: str, ts_content: str) -> dict:
    """
    Parses common Fig TypeScript completionSpec patterns into a clean JSON dict.
    Extracts name, description, subcommands, options.
    """
    spec = {
        "name": tool_name,
        "description": f"{tool_name} command line tool",
        "options": [],
        "subcommands": [],
    }

    # Extract top-level description
    desc_match = re.search(r'description:\s*["\']([^"\']+)["\']', ts_content)
    if desc_match:
        spec["description"] = desc_match.group(1)

    # Extract subcommands
    # e.g. name: "commit", description: "..."
    subcmd_blocks = re.findall(
        r'\{\s*name:\s*["\']([a-zA-Z0-9_\-]+)["\'],\s*description:\s*["\']([^"\']+)["\']',
        ts_content,
    )
    for name, desc in subcmd_blocks:
        spec["subcommands"].append({
            "name": name,
            "description": desc,
            "options": [],
        })

    # Extract options: name: ["-f", "--flag"] or name: "--flag"
    opt_blocks = re.findall(
        r'name:\s*(?:\[([^\]]+)\]|["\']([^"\']+)["\'])\s*,\s*description:\s*["\']([^"\']+)["\']',
        ts_content,
    )
    for names_arr, single_name, desc in opt_blocks:
        if names_arr:
            names = [n.strip().strip('"\'') for n in names_arr.split(",") if n.strip()]
        else:
            names = [single_name]
        spec["options"].append({
            "name": names,
            "description": desc,
        })

    return spec


def import_spec(tool_name: str, output_dir: Optional[Path] = None):
    out_dir = output_dir or SPECS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{tool_name.lower()}.json"

    ts_content = fetch_remote_ts_spec(tool_name)
    if not ts_content:
        print(f"❌ Failed to obtain spec for '{tool_name}'.")
        return False

    spec_data = parse_simple_ts_to_dict(tool_name, ts_content)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(spec_data, f, ensure_ascii=False, indent=2)

    print(f"✔ Successfully imported Fig spec for '{tool_name}'!")
    print(f"  📄 Saved to: {out_file.resolve()}")
    print(f"  📦 Subcommands: {len(spec_data.get('subcommands', []))}")
    print(f"  🚩 Options: {len(spec_data.get('options', []))}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and import specs from withfig/autocomplete into Kapsel."
    )
    parser.add_argument("tool", help="Name of tool to import (e.g. curl, kubectl, gh, rustc)")
    parser.add_argument(
        "--user",
        action="store_true",
        help="Save to user ~/.kapsel/registry/specs/ instead of builtin specs",
    )

    args = parser.parse_args()

    if args.user:
        from kapsel.core.completion.fig_engine import get_user_specs_dir
        out_dir = get_user_specs_dir()
    else:
        out_dir = SPECS_DIR

    import_spec(args.tool, out_dir)


if __name__ == "__main__":
    main()
