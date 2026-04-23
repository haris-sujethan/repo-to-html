## repo-to-html

Convert your repository into a single HTML document that you can save as a PDF. Main purpose is to give your LLMs full context of your project. 

- **No external libraries** — Python standard library, nothing to install
- **Safe for enterprise** — no network calls, runs offline, I use this at work
- **Flexible exclusions** — ignores build artifacts, lock files, binary files, and anything in your `.gitignore` automatically

This is the lightweight version (<350 lines). If you prefer a pip-installable CLI tool with more features I also built:

**[repo-2-pdf](https://github.com/haris-sujethan/repo-2-pdf)**

## How to use

```bash
python repo-to-html.py <repo_dir>

# Custom output path
python repo-to-html.py <repo_dir> -o output.html

# Custom title
python repo-to-html.py <repo_dir> -t "My Project"
```

The script generates a `repository.html` file in the same directory. From there, open it and hit `Ctrl+P`, and save as PDF.