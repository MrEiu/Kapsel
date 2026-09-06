"""
Kapsel Block Runner.
Executes multi-line command blocks in either sequential atomic mode
or parallel concurrent mode (triggered by -c).
All comments and docstrings are in English.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, List, Optional, Tuple

from rich.console import Console

from kapsel.core.block.model import CommandBlock
from kapsel.core.block.registry import get_block_registry


def split_commands(raw_text: str) -> List[str]:
    """
    Parses multi-line or delimited text into individual commands,
    ignoring empty lines and pure comments.
    """
    lines = raw_text.strip().splitlines()
    result: List[str] = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        result.append(cleaned)
    return result


def _run_single_command_process(cmd: str, cwd: str) -> Tuple[int, str, int]:
    """
    Executes a single command in a standalone subshell.
    Returns (exit_code, output_str, duration_ms).
    """
    t0 = time.perf_counter()
    shell = "pwsh.exe" if sys.platform == "win32" else "sh"
    try:
        if sys.platform == "win32":
            # Prefer pwsh, fallback to powershell or cmd
            proc = subprocess.run(
                ["pwsh.exe", "-NoLogo", "-Command", cmd],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
        else:
            proc = subprocess.run(
                ["/bin/sh", "-c", cmd],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
        t1 = time.perf_counter()
        ms = int((t1 - t0) * 1000)
        output = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, output, ms
    except Exception as e:
        t1 = time.perf_counter()
        ms = int((t1 - t0) * 1000)
        return 1, f"Execution failed: {e}\n", ms


def execute_sequential_block(
    commands: List[str],
    executor: Any,
    console: Optional[Console] = None,
) -> Tuple[int, str]:
    """
    Executes multiple commands sequentially within the same context.
    If a command fails, execution immediately halts to prevent dirty state.
    """
    con = console or Console(legacy_windows=False)
    combined_outputs: List[str] = []
    last_exit_code = 0
    t0 = time.perf_counter()

    for idx, cmd in enumerate(commands, 1):
        if len(commands) > 1:
            con.print(f"[dim]❯ [{idx}/{len(commands)}][/] [bold white]{cmd}[/]")

        exec_res = executor.execute(cmd)
        last_exit_code = exec_res.exit_code
        combined_outputs.append(f"$ {cmd} (exit {last_exit_code})\n")

        # Atomic failure stop
        if last_exit_code != 0:
            if len(commands) > 1:
                con.print(
                    f"[bold #f43f5e]✖ Command failed with exit code {last_exit_code}.[/] "
                    f"[dim]Aborting remaining {len(commands) - idx} command(s) in block.[/]\n"
                )
            break

    t1 = time.perf_counter()
    total_ms = int((t1 - t0) * 1000)

    # Register block
    full_cmd = "\n".join(commands)
    registry = get_block_registry()
    registry.add_block(
        command=full_cmd,
        exit_code=last_exit_code,
        duration_ms=total_ms,
        cwd=str(Path.cwd()),
        sub_commands=commands,
        is_concurrent=False,
        output_text="".join(combined_outputs),
    )

    return last_exit_code, "".join(combined_outputs)


def execute_parallel_block(
    commands: List[str],
    console: Optional[Console] = None,
    max_workers: int = 4,
) -> Tuple[int, str]:
    """
    Executes multiple commands concurrently in separate worker threads.
    Streams progress and collects individual task outputs.
    """
    con = console or Console(legacy_windows=False)
    if not commands:
        return 0, ""

    con.print(f"\n[bold #00f0ff]⚡ Kapsel Parallel Runner (kp -c)[/]")
    con.print(f"[dim]Spawning {len(commands)} concurrent tasks (max {max_workers} parallel workers)...[/]\n")

    current_cwd = str(Path.cwd())
    t0 = time.perf_counter()
    results: List[dict] = []

    with ThreadPoolExecutor(max_workers=min(len(commands), max_workers)) as pool:
        futures = {
            pool.submit(_run_single_command_process, cmd, current_cwd): (idx, cmd)
            for idx, cmd in enumerate(commands, 1)
        }

        for future in as_completed(futures):
            idx, cmd = futures[future]
            try:
                retcode, output, duration = future.result()
            except Exception as e:
                retcode, output, duration = 1, str(e), 0

            results.append({
                "index": idx,
                "command": cmd,
                "exit_code": retcode,
                "output": output,
                "duration_ms": duration,
            })

            icon = "[bold #10b981]✔[/]" if retcode == 0 else "[bold #f43f5e]✖[/]"
            con.print(f"  {icon} [cyan][{idx}/{len(commands)}][/] [bold white]{cmd}[/] [dim]({duration}ms, exit {retcode})[/]")
            if output.strip():
                # Indent output
                indented = "\n".join(f"    [dim]│[/] {line}" for line in output.strip().splitlines()[:6])
                con.print(indented)

    t1 = time.perf_counter()
    total_ms = int((t1 - t0) * 1000)

    # Sort results by original task index
    results.sort(key=lambda r: r["index"])
    max_exit = max(r["exit_code"] for r in results) if results else 0

    success_count = sum(1 for r in results if r["exit_code"] == 0)
    con.print(
        f"\n[dim]Summary:[/] [bold {'#10b981' if max_exit == 0 else '#f43f5e'}]{success_count}/{len(commands)} tasks succeeded[/] "
        f"[dim]in {total_ms}ms.[/]\n"
    )

    combined_output = "\n".join(
        f"--- Task {r['index']}: {r['command']} (exit {r['exit_code']}, {r['duration_ms']}ms) ---\n{r['output']}"
        for r in results
    )

    # Register block
    registry = get_block_registry()
    registry.add_block(
        command="\n".join(commands),
        exit_code=max_exit,
        duration_ms=total_ms,
        cwd=current_cwd,
        sub_commands=commands,
        is_concurrent=True,
        output_text=combined_output,
    )

    return max_exit, combined_output
