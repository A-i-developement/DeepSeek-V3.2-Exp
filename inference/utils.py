import os

def get_safe_path(base_dir: str, path: str, max_size: int = 0) -> str:
    """
    Validates a path against a base directory to prevent path traversal and optionally checks file size.

    Args:
        base_dir (str): Authorized base directory.
        path (str): Path to validate.
        max_size (int, optional): Maximum allowed file size in bytes. Defaults to 0 (no limit).

    Returns:
        str: The absolute, resolved path if valid.

    Raises:
        ValueError: If the path is outside the base directory.
        FileNotFoundError: If the file does not exist.
        RuntimeError: If the file size exceeds max_size.
    """
    safe_base = os.path.realpath(base_dir)
    target_path = os.path.realpath(os.path.join(safe_base, path))
    if os.path.commonpath([safe_base, target_path]) != safe_base:
        raise ValueError(f"Access denied: {path} is outside {base_dir}")
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"File not found: {target_path}")
    if max_size > 0 and os.path.getsize(target_path) > max_size:
        raise RuntimeError(f"File size exceeds limit: {target_path}")
    return target_path

def dist_print(*args, **kwargs):
    """
    Print only from the master rank (rank 0) in distributed settings.
    """
    if int(os.environ.get("RANK", "0")) == 0:
        print(*args, **kwargs)
