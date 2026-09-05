# Research and Investigation Rules

- **Strictly minimize ad-hoc `python -c` commands**:
  - Environment inspection (checking installed packages / versions) is acceptable when necessary.
  - Do NOT use ad-hoc python snippets to probe internal code logic, explore API signatures, or debug when static search tools are available.
- Always prioritize dedicated workspace tools:
  - Use `grep_search` and `view_file` to inspect code and module definitions directly.
  - Use `search_web` or documentation for external library specifications.

