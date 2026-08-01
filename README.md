# rename — Bulk File Rename Utility

A zero-dependency CLI tool for bulk file renaming. Supports prefix, suffix, string replace, and regex substitution. Always shows what changed. Dry-run mode (`-n`) lets you preview before committing. Portable across macOS, Linux, and WSL.

## Install

```bash
pip install git+https://github.com/jrbobbyhansen-pixel/rename.git
```

Or just copy `rename.py` anywhere on your `PATH`:

```bash
curl -O https://raw.githubusercontent.com/jrbobbyhansen-pixel/rename/main/rename.py
chmod +x rename.py
```

## Usage

```bash
# Add prefix to all markdown files
rename --prefix 'draft_' *.md

# Add suffix to text files
rename --suffix '_backup' *.txt

# Replace text in filenames
rename --replace 'old' 'new' *.jpg

# Regex substitution
rename --regex 's/\\d+//' *.log

# Dry-run: preview only
rename -n --prefix 'v2_' *
```

Exit code: `0` on success, `1` on error.

## Test

```bash
pip install pytest
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).

---

Part of the [Manta](https://github.com/jrbobbyhansen-pixel) collection — zero-dependency CLI tools for developers.
