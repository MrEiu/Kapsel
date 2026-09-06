"""
Unit tests for Kapsel search command, dynamic add completions, hidden command filtering,
and shore spec autocompletions.
All comments and descriptions are in English.
"""

from pathlib import Path
import sys
from rich.console import Console

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from kapsel.completion.kps.builtins.search import handle_search
from kapsel.completion.kps.registry import KpsCommandRegistry, get_kps_registry
from kapsel.completion.spec_manager import CarapaceSpecManager
import yaml


def test_search_command():
    console = Console(record=True)
    # Search all
    code = handle_search(["-a"], console=console)
    assert code == 0
    output = console.export_text()
    assert "Search Results" in output
    assert "kps init" in output
    assert "kps shore" in output
    assert "kps portal" in output

    # Fuzzy search with specific query
    console = Console(record=True)
    code = handle_search(["mirror"], console=console)
    assert code == 0
    output = console.export_text()
    assert "kps shore" in output


def test_hidden_commands_filtering():
    reg = get_kps_registry()
    visible_names = [c.name for c in reg.list_commands(include_hidden=False)]
    assert "setup-completion" not in visible_names
    assert "search" in visible_names
    assert "add" in visible_names

    # But still accessible via get()
    cmd = reg.get("setup-completion")
    assert cmd is not None
    assert cmd.hidden is True


def test_dynamic_add_completions():
    mgr = CarapaceSpecManager()
    kps_spec, kapsel_spec = mgr.build_aggregated_root_specs()

    # 'add' is a system command under 'kapsel', NOT 'kps'
    assert not any(c["name"] == "add" for c in kps_spec["commands"])

    add_cmd = None
    for cmd in kapsel_spec["commands"]:
        if cmd["name"] == "add":
            add_cmd = cmd
            break

    assert add_cmd is not None
    subcmd_names = [c["name"] for c in add_cmd.get("commands", [])]

    # Verify essential plugins and update are present
    assert "update" in subcmd_names
    assert "ai" in subcmd_names
    assert "alias" in subcmd_names
    assert "autopilot" in subcmd_names
    assert "fuck" in subcmd_names
    assert "help" in subcmd_names
    assert "init" in subcmd_names
    assert "install" in subcmd_names
    assert "portal" in subcmd_names
    assert "profile" in subcmd_names
    assert "rec" in subcmd_names
    assert "shore" in subcmd_names


def test_kapsel_and_kps_root_separation():
    mgr = CarapaceSpecManager()
    kps_spec, kapsel_spec = mgr.build_aggregated_root_specs()

    kps_cmd_names = {c["name"] for c in kps_spec["commands"]}
    kapsel_cmd_names = {c["name"] for c in kapsel_spec["commands"]}

    # System commands MUST exist under kapsel, and MUST NOT exist under kps
    for sys_cmd in ("status", "config", "datadir", "language", "toggle", "completion", "add"):
        assert sys_cmd in kapsel_cmd_names, f"{sys_cmd} should be in kapsel_spec"
        assert sys_cmd not in kps_cmd_names, f"{sys_cmd} should NOT be in kps_spec"

    # Tool plugins MUST exist under kps
    for tool_cmd in ("install", "update", "sync", "search", "help"):
        assert tool_cmd in kps_cmd_names, f"{tool_cmd} should be in kps_spec"



def test_shore_spec_completeness():
    shore_spec_path = root_dir / "plugins" / "shore" / "spec.yaml"
    assert shore_spec_path.exists()

    with open(shore_spec_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["name"] == "shore"
    cmd_map = {c["name"]: c for c in data.get("commands", [])}

    assert "set" in cmd_map
    assert "get" in cmd_map
    assert "reset" in cmd_map
    assert "measure" in cmd_map
    assert "list" in cmd_map
    assert "doctor" in cmd_map

    set_dishes = {d["name"]: d for d in cmd_map["set"].get("commands", [])}
    assert "python" in set_dishes
    assert "npm" in set_dishes
    assert "cargo" in set_dishes
    assert "docker" in set_dishes
    assert "brew" in set_dishes

    # Verify python has mirrors
    python_mirrors = [m["name"] for m in set_dishes["python"].get("commands", [])]
    assert "tuna" in python_mirrors
    assert "aliyun" in python_mirrors
    assert "ustc" in python_mirrors
    assert "first" in python_mirrors


def test_bare_kps_and_kapsel_completion_no_crash():
    """Verify 'kps ' and 'kapsel ' do not throw IndexError when followed by space."""
    from prompt_toolkit.document import Document
    from prompt_toolkit.completion import CompleteEvent
    from kapsel.completion.completer import DualStateCompleter

    completer = DualStateCompleter()

    # 1. 'kps '
    kps_cands = [c.text for c in completer.get_completions(Document("kps "), CompleteEvent())]
    assert len(kps_cands) > 0
    assert "search" in kps_cands or "install" in kps_cands

    # 2. 'kapsel '
    kapsel_cands = [c.text for c in completer.get_completions(Document("kapsel "), CompleteEvent())]
    assert len(kapsel_cands) > 0
    assert "status" in kapsel_cands or "config" in kapsel_cands


def test_native_plugin_completion_trailing_space():
    """Verify that plugin candidates without explicit start_position do not eat trailing space."""
    from unittest.mock import MagicMock
    from prompt_toolkit.document import Document
    from prompt_toolkit.completion import CompleteEvent
    from kapsel.completion.completer import DualStateCompleter

    mock_pm = MagicMock()
    # Plugin returns candidate without start_position
    mock_pm.get_plugin_completions.return_value = [{"text": "Kapsel"}]

    completer = DualStateCompleter(plugin_manager=mock_pm)

    # User typed 'z ' (ends with space)
    cands_space = list(completer.get_completions(Document("z "), CompleteEvent()))
    matching = [c for c in cands_space if c.text == "Kapsel"]
    assert len(matching) == 1
    # Must be 0 so trailing space is not deleted!
    assert matching[0].start_position == 0

    # User typed 'z kap' (does not end with space)
    cands_word = list(completer.get_completions(Document("z kap"), CompleteEvent()))
    matching_word = [c for c in cands_word if c.text == "Kapsel"]
    assert len(matching_word) == 1
    # Must be -len('kap') = -3
    assert matching_word[0].start_position == -3

