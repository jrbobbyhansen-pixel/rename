import os
import sys
import tempfile
import pytest

# Ensure the project root is on sys.path so we can import rename
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rename import apply_rename, resolve_files, run, build_parser


# ---------------------------------------------------------------------------
# apply_rename
# ---------------------------------------------------------------------------

def test_apply_rename_prefix():
    result = apply_rename("foo.txt", prefix="draft_")
    assert result == "draft_foo.txt"


def test_apply_rename_suffix():
    result = apply_rename("foo.txt", suffix="_backup")
    assert result == "foo_backup.txt"


def test_apply_rename_replace():
    result = apply_rename("foo-bar.txt", replace=("bar", "baz"))
    assert result == "foo-baz.txt"


def test_apply_rename_regex():
    result = apply_rename("report-2024.txt", regex=(r"\d+", "YYYY"))
    assert result == "report-YYYY.txt"


def test_apply_rename_unchanged():
    result = apply_rename("foo.txt", prefix="")
    assert result is None


def test_apply_rename_multiple_transforms():
    result = apply_rename("foo.txt", prefix="v2_", suffix="_final", replace=("foo", "bar"))
    assert result == "v2_bar_final.txt"


def test_apply_rename_no_ext():
    result = apply_rename("Makefile", prefix="old_")
    assert result == "old_Makefile"


def test_apply_rename_dotted_name():
    result = apply_rename("my.file.txt", prefix="pre_")
    assert result == "pre_my.file.txt"


# ---------------------------------------------------------------------------
# resolve_files
# ---------------------------------------------------------------------------

def test_resolve_files(tmp_path):
    (tmp_path / "a.txt").write_text("")
    (tmp_path / "b.txt").write_text("")
    (tmp_path / "c.md").write_text("")
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        files = resolve_files(["*.txt"])
        assert files == ["a.txt", "b.txt"]
    finally:
        os.chdir(cwd)


def test_resolve_files_no_match(tmp_path):
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        files = resolve_files(["*.xyz"])
        assert files == []
    finally:
        os.chdir(cwd)


# ---------------------------------------------------------------------------
# run (integration via dry-run)
# ---------------------------------------------------------------------------

def test_run_dry_run(capsys, tmp_path):
    (tmp_path / "foo.txt").write_text("hello")
    (tmp_path / "bar.txt").write_text("world")
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        parser = build_parser()
        args = parser.parse_args(["--prefix", "pre_", "--dry-run", "*.txt"])
        rc = run(args)
        assert rc == 0
        captured = capsys.readouterr()
        assert "~ foo.txt -> pre_foo.txt" in captured.out
        assert "~ bar.txt -> pre_bar.txt" in captured.out
        # Files should NOT have been renamed
        assert os.path.isfile("foo.txt")
        assert os.path.isfile("bar.txt")
    finally:
        os.chdir(cwd)


def test_run_actual_rename(tmp_path):
    (tmp_path / "foo.txt").write_text("hello")
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        parser = build_parser()
        args = parser.parse_args(["--prefix", "pre_", "*.txt"])
        rc = run(args)
        assert rc == 0
        assert not os.path.isfile("foo.txt")
        assert os.path.isfile("pre_foo.txt")
    finally:
        os.chdir(cwd)


def test_run_no_match(capsys, tmp_path):
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        parser = build_parser()
        args = parser.parse_args(["--prefix", "x_", "--dry-run", "*.nonexistent"])
        rc = run(args)
        assert rc == 1
        captured = capsys.readouterr()
        assert "no files matched" in captured.err
    finally:
        os.chdir(cwd)


def test_run_destination_exists(capsys, tmp_path):
    (tmp_path / "foo.txt").write_text("a")
    (tmp_path / "bar.txt").write_text("b")
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        parser = build_parser()
        args = parser.parse_args(["--replace", "foo", "bar", "*.txt"])
        rc = run(args)
        assert rc == 1
        captured = capsys.readouterr()
        assert "destination already exists" in captured.err
    finally:
        os.chdir(cwd)


def test_run_no_transform_errors():
    with pytest.raises(SystemExit):
        from rename import main
        main(["*.txt"])


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------

def test_version(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "rename 1.0.0" in captured.out
