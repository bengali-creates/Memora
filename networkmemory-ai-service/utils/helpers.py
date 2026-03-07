"""
Helper utility functions

Why separate utilities:
1. Reusable across modules
2. Easier testing
3. Clean separation of concerns
"""

import os
import time
from typing import Callable, Any
from functools import wraps


def timeit(func: Callable) -> Callable:
    """
    Decorator to measure function execution time

    Usage:
        @timeit
        def my_function():
            # do something

    This will print: "my_function took 1.23s"
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} took {elapsed:.2f}s")
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} took {elapsed:.2f}s")
        return result

    # Return appropriate wrapper based on whether function is async
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def ensure_dir(directory: str) -> str:
    """
    Ensure directory exists, create if not

    Args:
        directory: Path to directory

    Returns:
        Absolute path to directory
    """
    os.makedirs(directory, exist_ok=True)
    return os.path.abspath(directory)


def clean_text(text: str) -> str:
    """
    Clean and normalize text

    - Remove extra whitespace
    - Normalize line breaks
    - Strip leading/trailing space
    """
    # Replace multiple spaces with single space
    text = " ".join(text.split())
    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip
    text = text.strip()
    return text


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format

    Examples:
        45 -> "45s"
        90 -> "1m 30s"
        3665 -> "1h 1m 5s"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:  # Always show seconds if nothing else
        parts.append(f"{secs}s")

    return " ".join(parts)


def safe_filename(filename: str) -> str:
    """
    Convert string to safe filename

    Removes/replaces characters that are problematic in filenames
    """
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Remove or replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "")
    return filename


# Example usage
if __name__ == "__main__":
    # Test timeit decorator
    @timeit
    def slow_function():
        time.sleep(1)
        return "done"

    result = slow_function()
    print(f"Result: {result}")

    # Test other utilities
    print(f"\nDuration: {format_duration(3665)}")
    print(f"Safe filename: {safe_filename('My File: <test>.txt')}")
    print(f"Cleaned text: '{clean_text('  too   much    space  ')}'")
