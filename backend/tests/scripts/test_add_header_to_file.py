# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/tests/scripts/test_add_header_to_file.py

from pathlib import Path

from scripts.python.add_header_to_file import main


def run(tmp_path: Path, content: str, suffix=".py", subdir="app") -> str:
    file = tmp_path / subdir / f"test{suffix}"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)

    main([str(file)])
    return file.read_text()


def test_add_header_when_missing(tmp_path):
    content = "import logging\n"
    result = run(tmp_path, content)

    assert result == (
        "# SPDX-License-Identifier: AGPL-3.0-or-later\n"
        "# File: " + str(tmp_path / "app/test.py").replace("\\", "/") + "\n"
        "\n"
        "import logging\n"
    )


def test_replace_outdated_file_path(tmp_path):
    content = (
        "# SPDX-License-Identifier: AGPL-3.0-or-later\n"
        "# File: old/path.py\n"
        "\n"
        "import logging\n"
    )

    result = run(tmp_path, content)

    assert "old/path.py" not in result
    assert "test.py" in result
    assert result.count("SPDX-License-Identifier") == 1


def test_no_duplicate_header(tmp_path):
    content = (
        "# SPDX-License-Identifier: AGPL-3.0-or-later\n"
        "# File: app/test.py\n"
        "\n"
        "import logging\n"
    )

    result = run(tmp_path, content)

    assert result.count("SPDX-License-Identifier") == 1
    assert result.count("# File:") == 1


def test_exactly_one_blank_line_after_header(tmp_path):
    content = (
        "# SPDX-License-Identifier: AGPL-3.0-or-later\n"
        "# File: something.py\n"
        "\n"
        "\n"
        "\n"
        "import logging\n"
    )

    result = run(tmp_path, content)

    header, body = result.split("\n\n", 1)
    assert not body.startswith("\n")  # only one blank line


def test_preserve_shebang(tmp_path):
    content = "#!/usr/bin/env python3\n\nprint('hello')\n"

    result = run(tmp_path, content, subdir="scripts")

    assert result.startswith("#!/usr/bin/env python3\n")
    assert result.count("SPDX-License-Identifier") == 1


def test_idempotence(tmp_path):
    content = "import logging\n"

    file = tmp_path / "app/test.py"
    file.parent.mkdir(parents=True)
    file.write_text(content)

    main([str(file)])
    first = file.read_text()

    main([str(file)])
    second = file.read_text()

    assert first == second
