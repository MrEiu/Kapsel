"""
Kapsel Language Command: 'kapsel language [lang]'.
Displays active language or switches between supported world languages:
- en: English (default)
- zh_CN: Simplified Chinese
- ja: Japanese
- es: Spanish
- fr: French
- de: German
- ru: Russian
All comments and descriptions are in English.
"""

from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kapsel.i18n import (
    SUPPORTED_LANGUAGES,
    _,
    get_current_language,
    normalize_language_code,
    set_current_language,
)
from kapsel.ui.banner import ensure_utf8_io


def handle_language_command(args: Optional[List[str]] = None, console: Optional[Console] = None) -> int:
    """
    Handles 'kapsel language' and 'kps language'.
    Without arguments: displays supported languages table and active language badge.
    With arguments: switches current language and persists setting to ~/.kapsel/config.yaml.
    """
    ensure_utf8_io()
    con = console or Console(legacy_windows=False)
    current_code = get_current_language()

    if not args:
        # Render language selection table
        curr_info = SUPPORTED_LANGUAGES.get(current_code, {"name": current_code, "native": current_code})

        grid = Table(title=f"🌐 {_('Available Languages')}", box=None, title_justify="left", padding=(0, 2))
        grid.add_column(_("Code"), style="bold #00f0ff", width=12)
        grid.add_column(_("Language"), style="#e4e4e7", width=22)
        grid.add_column(_("Native Name"), style="bold #a855f7", width=20)
        grid.add_column(_("Aliases"), style="dim #9ca3af")
        grid.add_column(_("Status"), width=12)

        for code, meta in SUPPORTED_LANGUAGES.items():
            aliases_str = ", ".join(meta.get("aliases", []))
            is_curr = (code == current_code)
            status_str = f"[bold #10b981]✔ {_('Active')}[/]" if is_curr else ""
            grid.add_row(code, meta["name"], meta["native"], aliases_str, status_str)

        con.print()
        con.print(grid)
        con.print()
        con.print(f"[dim]{_('Usage:')} [/][bold #38bdf8]kps language <code/alias>[/] [dim](e.g. 'kps language zh' or 'kps language ja')[/]\n")
        return 0

    target_raw = args[0].strip()
    target_code = normalize_language_code(target_raw)

    if not target_code or target_code not in SUPPORTED_LANGUAGES:
        available = ", ".join(SUPPORTED_LANGUAGES.keys())
        err_msg = _("Error: Unsupported language '{input}'. Available codes: {available}").format(
            input=target_raw, available=available
        )
        con.print(f"[bold #f43f5e]{err_msg}[/]")
        return 1

    success = set_current_language(target_code, persist=True)
    if success:
        # Re-sync Carapace declarative completion specifications with the new language
        try:
            from kapsel.completion.spec_manager import CarapaceSpecManager
            from kapsel.completion.carapace_engine import get_carapace_engine

            CarapaceSpecManager().sync_specs(force=True)
            get_carapace_engine().reload_tools()
        except Exception:
            pass

        meta = SUPPORTED_LANGUAGES[target_code]
        msg = _("✔ Language successfully switched to: {name} ({code})").format(
            name=meta["native"], code=target_code
        )
        con.print(f"[bold #10b981]{msg}[/]")
        return 0
    else:
        con.print(f"[bold #f43f5e]Failed to update language setting.[/]")
        return 1
