#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/scripts/python/add_header_to_file.py

import sys
from pathlib import Path

LICENSE = "AGPL-3.0-or-later"
DEFAULT_SHEBANG = "#!/usr/bin/env python3\n"

COMMENT = {
    ".py": "#",
    ".ts": "//",
    ".tsx": "//",
    ".js": "//",
    ".jsx": "//",
}


def is_under_backend_scripts(path: Path) -> bool:
    parts = path.parts
    return any(
        parts[i] == "backend" and parts[i + 1] == "scripts"
        for i in range(len(parts) - 1)
    )


def is_under_backend_tests(path: Path) -> bool:
    parts = path.parts
    return any(
        parts[i] == "backend" and parts[i + 1] == "tests" for i in range(len(parts) - 1)
    )


def is_executable_script(path: Path, *, has_shebang: bool) -> bool:
    """Return True if the file should be treated as a runnable script.

    Rules:
    - never for backend/tests/**
    - yes if it already has a shebang
    - yes if it is executable
    - yes if it lives under backend/scripts/**
    """
    is_executable = (path.stat().st_mode & 0o111) != 0

    if is_under_backend_tests(path):
        return False

    return has_shebang or is_executable or is_under_backend_scripts(path)


def skip_blank_lines(lines: list[str], idx: int) -> int:
    """Return the next index after consecutive blank lines."""
    while idx < len(lines) and lines[idx] == "\n":
        idx += 1
    return idx


def main(paths: list[str]) -> int:
    changed = False

    for raw in paths:
        path = Path(raw)
        if not path.is_file() or path.suffix not in COMMENT:
            continue

        prefix = COMMENT[path.suffix]
        spdx = f"{prefix} SPDX-License-Identifier: {LICENSE}\n"
        file_line = f"{prefix} File: {path.as_posix()}\n"
        header = [spdx, file_line]

        lines = path.read_text().splitlines(keepends=True)
        new_lines: list[str] = []
        idx = 0

        # --- Shebang handling
        has_shebang = bool(lines and lines[0].startswith("#!"))

        if is_under_backend_tests(path):
            # Strip shebangs entirely in tests
            if has_shebang:
                idx = 1
        else:
            if is_executable_script(path=path, has_shebang=has_shebang):
                if has_shebang:
                    new_lines.append(lines[0])
                    idx = 1
                else:
                    new_lines.append(DEFAULT_SHEBANG)

        # --- Skip blank lines after shebang ---
        idx = skip_blank_lines(lines, idx)

        # --- Remove existing SPDX header (idempotent core) ---
        def is_spdx(line: str) -> bool:
            return "SPDX-License-Identifier:" in line

        def is_file_line(line: str, *, prefix: str = prefix) -> bool:
            return line.lstrip().startswith(f"{prefix} File:")

        if idx < len(lines) and is_spdx(lines[idx]):
            idx += 1
            if idx < len(lines) and is_file_line(lines[idx]):
                idx += 1

            # Skip blank lines after old header
            while idx < len(lines) and lines[idx] == "\n":
                idx += 1

        # --- Insert canonical header ---
        new_lines.extend(header)

        # Skip existing blank lines before code
        idx = skip_blank_lines(lines, idx)

        # Detect next top-level statement
        next_line = lines[idx] if idx < len(lines) else ""

        if next_line.lstrip().startswith(("def ", "class ")):
            # PEP 8: two blank lines before top-level defs/classes
            new_lines.append("\n")
            new_lines.append("\n")
        else:
            # Default: one blank line
            new_lines.append("\n")

        new_lines.extend(lines[idx:])

        # --- Normalize EOF: exactly one trailing newline ---
        text = "".join(new_lines).rstrip("\n") + "\n"

        if text != "".join(lines):
            path.write_text(text)
            print(f"Updated header: {path}")
            changed = True

    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
