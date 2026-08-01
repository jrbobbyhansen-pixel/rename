# rename

A zero-dependency CLI tool for bulk file renaming. Supports prefix, suffix, string replace, and regex substitution. Always shows what changed. Dry-run mode (`-n`) lets you preview before committing.

```bash
pip install git+https://github.com/jrbobbyhansen-pixel/rename.git

rename --prefix 'draft_' *.md
rename --suffix '_backup' *.txt
rename --replace 'old' 'new' *.jpg
rename --regex 's/\d+//' *.log
rename -n --prefix 'v2_' *        # dry-run: preview only
```
