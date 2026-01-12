# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/scripts/test_add_header_to_file_shebang.py

from __future__ import annotations

from pathlib import Path

from scripts.python.add_header_to_file import main


def _write(tmp_path: Path, rel: str, content: str) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_no_shebang_added_in_backend_tests_scripts(tmp_path: Path) -> None:
    """
    Regression test: `backend/tests/scripts/...` must NOT be treated as a runnable script
    just because it contains a `scripts` directory in the path.
    """
    p = _write(
        tmp_path,
        "backend/tests/scripts/test_add_header.py",
        "import logging\n",
    )

    main([str(p)])

    text = p.read_text()
    assert not text.startswith("#!"), text
    assert text.count("SPDX-License-Identifier:") == 1
    assert text.count("# File:") == 1


def test_shebang_added_in_backend_scripts_even_if_not_executable(
    tmp_path: Path,
) -> None:
    """
    If you decided that anything under `backend/scripts/` is a script, ensure a shebang is inserted
    even when the file mode is -rw-r--r-- (non-executable).
    """
    p = _write(
        tmp_path,
        "backend/scripts/python/tool.py",
        "print('hi')\n",
    )

    # Ensure it's not executable (default is usually 0o644, but force it)
    p.chmod(0o644)

    main([str(p)])

    text = p.read_text()
    assert text.startswith("#!/usr/bin/env python3\n"), text
    assert text.count("SPDX-License-Identifier:") == 1
    assert text.count("# File:") == 1


def test_absolute_path_detection_backend_scripts(tmp_path: Path) -> None:
    """
    The detection must work when the path passed to main() is absolute.
    This guards against brittle checks like `path.parts[:2] == ('backend', 'scripts')`.
    """
    p = _write(
        tmp_path,
        "backend/scripts/python/abs_tool.py",
        "print('abs')\n",
    )
    p.chmod(0o644)

    main([str(p.resolve())])

    text = p.read_text()
    assert text.startswith("#!/usr/bin/env python3\n"), text


def test_absolute_path_detection_backend_tests_scripts(tmp_path: Path) -> None:
    """
    Same as above, but for the tests path: even with an absolute path,
    `backend/tests/scripts/...` must not receive a shebang.
    """
    p = _write(
        tmp_path,
        "backend/tests/scripts/abs_test.py",
        "import os\n",
    )
    p.chmod(0o644)

    main([str(p.resolve())])

    text = p.read_text()
    assert not text.startswith("#!"), text


def test_strip_shebang_in_backend_tests(tmp_path: Path) -> None:
    """
    Files under backend/tests/** must not have a shebang,
    even if one was previously present.
    """
    p = _write(
        tmp_path,
        "backend/tests/scripts/has_shebang.py",
        "#!/usr/bin/env python3\n\nprint('already')\n",
    )
    p.chmod(0o644)

    main([str(p)])

    text = p.read_text()

    assert not text.startswith("#!"), text
    assert text.count("#!/usr/bin/env python3") == 0
    assert text.count("SPDX-License-Identifier:") == 1
    assert text.count("# File:") == 1


def test_idempotence_with_shebang_logic(tmp_path: Path) -> None:
    """
    Running twice should produce no changes, including around shebang insertion.
    """
    p = _write(
        tmp_path,
        "backend/scripts/python/idempotent_tool.py",
        "print('x')\n",
    )
    p.chmod(0o644)

    main([str(p)])
    first = p.read_text()

    main([str(p)])
    second = p.read_text()

    assert first == second
