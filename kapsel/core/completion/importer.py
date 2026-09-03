"""
Fig Spec Importer & Converter Service.
Fetches and converts completion specs from withfig/autocomplete (or local files)
directly into Kapsel Fig.Spec JSON format.
"""

import json
from pathlib import Path
import re
import sys
from typing import Optional
import urllib.request

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/withfig/autocomplete/master/src"


def fetch_remote_ts_spec(tool_name: str) -> Optional[str]:
    url = f"{GITHUB_RAW_BASE}/{tool_name}.ts"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Kapsel/0.2.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8")
    except Exception:
        pass
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

    # Extract subcommands: e.g. { name: "commit", description: "..." }
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


def import_fig_spec(tool_name: str, output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{tool_name.lower()}.json"

    ts_content = fetch_remote_ts_spec(tool_name)
    if not ts_content:
        return False

    spec_data = parse_simple_ts_to_dict(tool_name, ts_content)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(spec_data, f, ensure_ascii=False, indent=2)

    return True
