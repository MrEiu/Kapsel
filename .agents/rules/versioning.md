# Kapsel & Plugin Version Iteration Rules

## Base-10 Decimal Rollover Rule (逢 9 进 1)
Whenever modifying Kapsel core code or any plugin in this repository:
1. **Always increment the version number**: Never commit functional code modifications or bug fixes without advancing the version.
2. **Rollover on 9**: Always follow the base-10 decimal incrementing convention:
   - `0.1.8` -> `0.1.9` -> `0.2.0` (carry over to minor upon reaching 9)
   - `0.2.8` -> `0.2.9` -> `0.3.0`
   - `0.9.9` -> `1.0.0`
3. **Synchronization Checklist**:
   - For Kapsel core: Update version in `pyproject.toml` and `kapsel/__init__.py`.
   - For plugins: Update `version` in `PluginManifest(...)` inside `plugins/<name>/plugin.py`, and update the version and changelog entry in `plugins/catalog.json`.
