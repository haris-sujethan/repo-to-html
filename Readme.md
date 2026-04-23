Convert your repository into a single HTML document that you can save as a PDF. Main purpose is to give your LLMs full context of your project. This is the lightweight version (<350 lines). If you prefer a pip-installable CLI tool with more features I also built:

**[repo-2-pdf](https://github.com/haris-sujethan/repo-2-pdf)**

---

- **No external libraries** — pure Python standard library, nothing to install
- **Safe for enterprise** — no network calls, runs fully offline, no security concerns
- **Flexible exclusions** — ignores build artifacts, lock files, binary files, and anything in your `.gitignore` automatically
- **Fast to PDF** — HTML → Chrome print dialog → Save as PDF, done

---

## How to use

```bash
python repo-to-html.py <repo_dir>

# Custom output path
python repo-to-html.py <repo_dir> -o output.html

# Custom title
python repo-to-html.py <repo_dir> -t "My Project"
```

The script generates a `repository.html` file in the same directory. From there, open it in Chrome or Edge, hit `Ctrl+P`, and save as PDF.

---

## What gets excluded

The script automatically skips:

- Binary and media files (images, fonts, executables, archives)
- Build and dependency folders (`node_modules`, `dist`, `venv`, `.git`, etc.)
- Lock files and secrets (`.env`, `package-lock.json`, `yarn.lock`, etc.)
- Anything matched by your `.gitignore`
- Files over 500 KB
