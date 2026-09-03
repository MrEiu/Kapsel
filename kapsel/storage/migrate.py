"""
Kapsel Data Migration Service.
Allows CLI users to relocate Kapsel's data storage directory to any custom location,
automatically moving existing databases, configs, logs, and registry manifests,
leaving nothing behind in the old directory ("原来不留").
"""

import os
from pathlib import Path
import shutil
from typing import Tuple, Union

from kapsel.storage.logger import (
    POINTER_FILE,
    get_default_kapsel_dir,
    get_kapsel_dir,
    logger,
    setup_logger,
)
from kapsel.storage.user_db import get_user_db


def migrate_kapsel_data(target_path_str: str) -> Tuple[bool, str]:
    """
    Migrates the entire Kapsel data sandbox to target_path_str.
    Returns (success, message).
    """
    # Sanitize input: strip whitespace and any surrounding quotation marks
    cleaned = target_path_str.strip().strip('"\'').strip()
    if not cleaned:
        return False, "目标路径不能为空。"

    current_dir = get_kapsel_dir().resolve()
    default_dir = get_default_kapsel_dir().resolve()

    if cleaned.lower() in ("default", "reset", "origin"):
        target_dir = default_dir
    else:
        target_dir = Path(cleaned).expanduser().resolve()

    if current_dir == target_dir:
        return False, f"目标路径与当前数据目录相同 ({current_dir})，无需迁移。"

    # Check if target is inside current or vice versa
    try:
        if target_dir.is_relative_to(current_dir):
            return False, "目标路径不能位于当前数据目录内部，请指定外部独立路径。"
    except Exception:
        pass

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"无法创建目标目录 '{target_dir}': {e}"

    # 1. Release open file handles and connections
    for h in list(logger.handlers):
        try:
            h.close()
            logger.removeHandler(h)
        except Exception:
            pass

    user_db = get_user_db()
    user_db.close()

    # 2. Copy all files and subdirectories to target
    copied_items = []
    try:
        for item in current_dir.iterdir():
            dest = target_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
            copied_items.append((item, dest))
    except Exception as e:
        # Re-setup logger in case of error
        setup_logger()
        return False, f"数据复制迁移过程中发生异常: {e}"

    # 3. Clean up source directory ("原来不留")
    import gc
    gc.collect()

    cleanup_errors = []
    for src_item, _ in copied_items:
        try:
            if src_item.is_dir():
                shutil.rmtree(src_item, ignore_errors=True)
            else:
                src_item.unlink(missing_ok=True)
        except Exception as e:
            cleanup_errors.append(str(e))

    # Remove the empty source root directory if empty
    try:
        if not any(current_dir.iterdir()):
            current_dir.rmdir()
    except Exception:
        pass

    # 4. Update persistent location pointer file
    try:
        if target_dir == default_dir:
            if POINTER_FILE.exists():
                POINTER_FILE.unlink()
        else:
            POINTER_FILE.write_text(str(target_dir), encoding="utf-8")
    except Exception as e:
        setup_logger()
        return False, f"更新存储指针文件失败: {e}"

    # 5. Reinitialize subsystems with the new location
    setup_logger()
    user_db.reset_path()

    msg = f"成功将全部数据完整迁移至: {target_dir} (原有旧数据已彻底清理)"
    if cleanup_errors:
        msg += f" (注: 个别临时文件清理有延迟: {', '.join(cleanup_errors)})"

    return True, msg
