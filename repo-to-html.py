import argparse
import datetime
import fnmatch
import html
import os
import sys

EXCLUDED_EXTENSIONS = {
    ".pyc", ".class", ".o", ".exe", ".dll", ".so", ".dylib",
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg",
    ".webp", ".bmp", ".tiff",
    ".ttf", ".woff", ".woff2", ".eot",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".map", ".lock", ".db", ".sqlite",
}

EXCLUDED_FOLDERS = {
    ".git", ".hg", ".svn",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".pnp",
    "venv", ".venv", "env",
    "dist", "build", "out", ".next", ".nuxt", ".output",
    ".vercel", ".netlify",
    ".cache", "coverage", ".nyc_output",
    ".vscode", ".idea",
    "repo-export",
}

EXCLUDED_FILES = {
    ".env", ".env.local", ".env.production",
    "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "poetry.lock",
    "Pipfile.lock", "Gemfile.lock", "composer.lock",
    os.path.basename(__file__),
}

MAX_FILE_SIZE_KB = 500

def load_gitignore(repo_dir: str) -> list:
    gitignore_path = os.path.join(repo_dir, ".gitignore")
    patterns = []
    if not os.path.isfile(gitignore_path):
        return patterns

    with open(gitignore_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")

            if not line or line.startswith("#"):
                continue

            negation = line.startswith("!")
            if negation:
                line = line[1:]

            dir_only = line.endswith("/")
            if dir_only:
                line = line.rstrip("/")

            if line.startswith("/"):
                line = line.lstrip("/")

            patterns.append((line, dir_only, negation))

    print(f"  .gitignore loaded ({len(patterns)} patterns)", file=sys.stderr)
    return patterns

def is_gitignored(rel_path: str, patterns: list, is_dir: bool = False) -> bool:
    if not patterns:
        return False

    ignored = False
    name = rel_path.split("/")[-1]

    for pattern, dir_only, negation in patterns:
        if dir_only and not is_dir:
            continue

        matched = (
            fnmatch.fnmatch(name, pattern)
            or fnmatch.fnmatch(rel_path, pattern)
            or fnmatch.fnmatch(rel_path, f"**/{pattern}")
        )

        if matched:
            ignored = not negation

    return ignored

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }}
        header h1 {{
            color: #2c3e50;
            margin: 0 0 4px 0;
        }}
        header p {{
            margin: 0;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .toc {{
            background-color: #f8f9fa;
            padding: 15px 20px;
            margin-bottom: 30px;
            border: 1px solid #eee;
        }}
        .toc h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .toc ol {{
            padding-left: 20px;
            margin: 0;
        }}
        .toc li {{
            margin-bottom: 4px;
            font-size: 0.95em;
        }}
        .toc a {{
            text-decoration: none;
            color: #3498db;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
        .file-title {{
            background-color: #f0f0f0;
            padding: 10px 12px;
            margin-top: 30px;
            margin-bottom: 0;
            border-left: 4px solid #3498db;
            font-weight: bold;
            font-family: Consolas, Monaco, "Andale Mono", monospace;
            font-size: 13px;
            word-break: break-all;
        }}
        .file-content {{
            background-color: #f9f9f9;
            padding: 15px;
            border: 1px solid #eee;
            border-top: none;
            font-family: Consolas, Monaco, "Andale Mono", monospace;
            font-size: 13px;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            word-break: normal;
            hyphens: none;
        }}
        .footer {{
            margin-top: 50px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                padding: 0;
                font-size: 10pt;
            }}
            .toc {{
                break-after: page;
            }}
            .file-title {{
                break-after: avoid;
                font-size: 8pt;
            }}
            .file-content {{
                font-size: 7.5pt;
                border: 1px solid #ccc;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p>Generated on {date} &nbsp;&bull;&nbsp; {file_count} files</p>
        </header>

        <div class="toc">
            <h2>Table of Contents</h2>
            <ol>
                {toc_items}
            </ol>
        </div>

        {file_blocks}

        <div class="footer">
            <p>Made by Haris</p>
        </div>
    </div>
</body>
</html>
"""

def add_break_hints(text: str) -> str:
    out = text.replace("-", "-\u200b")
    out = out.replace("#[", "#\u2060[")
    return out

def should_include(file_path: str, repo_dir: str, gitignore: list) -> bool:
    name = os.path.basename(file_path)

    if name in EXCLUDED_FILES:
        return False

    _, ext = os.path.splitext(name)
    if ext.lower() in EXCLUDED_EXTENSIONS:
        return False

    try:
        rel = os.path.relpath(file_path, repo_dir)
    except ValueError:
        rel = file_path

    rel_fwd = rel.replace("\\", "/")
    parts = rel_fwd.split("/")

    for part in parts[:-1]:
        if part in EXCLUDED_FOLDERS:
            return False

    for i, part in enumerate(parts):
        segment_path = "/".join(parts[: i + 1])
        is_dir = i < len(parts) - 1
        if is_gitignored(segment_path, gitignore, is_dir=is_dir):
            return False

    try:
        if os.path.getsize(file_path) / 1024 > MAX_FILE_SIZE_KB:
            print(f"  skip  (>{MAX_FILE_SIZE_KB} KB)  {rel_fwd}", file=sys.stderr)
            return False
    except OSError:
        return False

    return True


def build_html(repo_dir: str, title: str) -> str:
    toc_parts = []
    block_parts = []
    file_count = 0

    gitignore = load_gitignore(repo_dir)

    for root, dirs, files in os.walk(repo_dir, topdown=True):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_FOLDERS)

        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, repo_dir).replace("\\", "/")

            if not should_include(fpath, repo_dir, gitignore):
                continue

            file_count += 1
            fid = f"file-{file_count}"

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                    raw = fh.read()
            except OSError as exc:
                print(f"  error {rel}: {exc}", file=sys.stderr)
                continue

            toc_parts.append(
                f'<li><a href="#{fid}">{html.escape(rel)}</a></li>'
            )

            hinted = add_break_hints(raw)

            block_parts.append(
                f'<div class="file-title" id="{fid}">{html.escape(rel)}</div>\n'
                f'<div class="file-content">{html.escape(hinted)}</div>'
            )

            print(f"  ok  {rel}", file=sys.stderr)

    return HTML_TEMPLATE.format(
        title=html.escape(title),
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        file_count=file_count,
        toc_items="\n                ".join(toc_parts),
        file_blocks="\n\n        ".join(block_parts),
    )

def main():
    parser = argparse.ArgumentParser(
        description="Convert a repository to a single HTML file optimised for PDF export."
    )
    parser.add_argument("repo_dir", help="Path to the repository directory")
    parser.add_argument(
        "-o", "--output",
        default="repository.html",
        help="Output file (default: repository.html)",
    )
    parser.add_argument(
        "-t", "--title",
        default=None,
        help="Document title (defaults to repo folder name)",
    )
    args = parser.parse_args()

    repo_dir = os.path.abspath(args.repo_dir)
    if not os.path.isdir(repo_dir):
        print(f"Error: '{repo_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    title = args.title or os.path.basename(repo_dir)
    output = os.path.abspath(args.output)

    print(f"Scanning: {repo_dir}", file=sys.stderr)
    html_content = build_html(repo_dir, title)

    with open(output, "w", encoding="utf-8") as fh:
        fh.write(html_content)

    print(f"\nDone → {output}", file=sys.stderr)

if __name__ == "__main__":
    main()