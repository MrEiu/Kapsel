"""
Kapsel terminal-level routing and parameter injection engine.
Translates Linux-First aliases to host shell native commands with multi-tier fallback.
"""

from dataclasses import dataclass
import re
from typing import Optional, Tuple

from kapsel.storage.commands import CommandEntry, CommandRegistry
from kapsel.storage.logger import logger


@dataclass
class TranslationResult:
    original_input: str
    alias: str
    args: str
    desc: str
    target_shell: str
    translated_cmd: str
    template: str


class CommandRouter:
    """Routes and translates kps commands for the current terminal."""

    def __init__(self, registry: CommandRegistry, current_shell: str):
        self.registry = registry
        self.current_shell = current_shell

    def set_shell(self, shell: str) -> None:
        self.current_shell = shell

    def translate(self, input_line: str) -> Optional[TranslationResult]:
        """
        Translates a 'kps ...' command line to the target shell command.
        Example: 'kps rm -rf node_modules' -> 'Remove-Item -Recurse -Force node_modules'
        """
        stripped = input_line.strip()
        if not stripped.startswith("kps"):
            return None

        # Strip 'kps' or 'kps ' prefix
        body = stripped[3:].strip()
        if not body:
            return None

        match = self.registry.find_best_match(body)
        if not match:
            # Fallback: execute body directly if no mapping exists
            logger.debug(f"No specific mapping found for '{body}', passing through directly.")
            return TranslationResult(
                original_input=input_line,
                alias=body.split()[0] if body else "",
                args=" ".join(body.split()[1:]) if len(body.split()) > 1 else "",
                desc="原生透传执行",
                target_shell=self.current_shell,
                translated_cmd=body,
                template=body,
            )

        entry, raw_args = match
        template = entry.get_template_for_shell(self.current_shell)
        if not template:
            template = body

        translated = self._inject_args(template, raw_args)

        return TranslationResult(
            original_input=input_line,
            alias=entry.alias,
            args=raw_args,
            desc=entry.desc,
            target_shell=self.current_shell,
            translated_cmd=translated,
            template=template,
        )

    def preview(self, input_line: str) -> Optional[str]:
        """
        Generates a quick preview string of what the translated command will be.
        Used by the interactive completion UI.
        """
        res = self.translate(input_line)
        return res.translated_cmd if res else None

    @staticmethod
    def _inject_args(template: str, args: str) -> str:
        """
        Safely replaces {{args}} placeholder or appends arguments.
        Clean up double spaces if args are empty.
        """
        args_clean = args.strip()
        if "{{args}}" in template:
            if args_clean:
                result = template.replace("{{args}}", args_clean)
            else:
                result = template.replace("{{args}}", "").strip()
        else:
            if args_clean:
                result = f"{template} {args_clean}"
            else:
                result = template

        # Normalize multiple spaces into single space
        return re.sub(r"\s+", " ", result).strip()
