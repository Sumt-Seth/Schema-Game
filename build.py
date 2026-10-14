"""Bundle Deep Schema into one self-contained index.html.

    python build.py        ->  index.html

The source (dev.html, styles.css, src/, config/) uses ES modules, which browsers only
load over http(s), so dev.html needs a local server (VS Code Live Server, or
python -m http.server). index.html has every module and the CSS inlined, so it works
anywhere: double-clicked from your computer, on GitHub Pages, or sent as one file.
Run this after every change to the source. Python 3 standard library only.
"""
import os
import posixpath
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
IMPORT_RE = re.compile(r'^import (\{[^}]*\}|\* as \w+) from "([^"]+)";\n', re.M)
EXPORT_RE = re.compile(r'^export \{(.*?)\};\s*$', re.M | re.S)


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def resolve(frm, spec):
    return posixpath.normpath(posixpath.join(posixpath.dirname(frm), spec))


def collect(entry):
    """Modules in dependency order (each one after everything it imports)."""
    order, seen = [], set()

    def visit(path):
        if path in seen:
            return
        seen.add(path)
        for _, spec in IMPORT_RE.findall(read(path)):
            visit(resolve(path, spec))
        order.append(path)

    visit(entry)
    return order


def convert(path):
    """Turn one ES module into a bundle entry: imports become __mods lookups, export becomes return."""
    text = read(path)

    def imp(m):
        names, spec = m.group(1), m.group(2)
        target = resolve(path, spec)
        if names.startswith("*"):
            names = names.split(" as ")[1]
        return f'const {names} = __mods["{target}"];\n'

    text = IMPORT_RE.sub(imp, text)
    m = EXPORT_RE.search(text)
    exports = m.group(1).strip() if m else ""
    if m:
        text = text[:m.start()].rstrip() + "\n"
    return f'/* ===== {path} ===== */\n__mods["{path}"] = (() => {{\n{text}\nreturn {{ {exports} }};\n}})();\n'


def build():
    modules = collect("src/main.js")
    js = '(() => {\n"use strict";\nconst __mods = {};\n' + "\n".join(convert(p) for p in modules) + "})();\n"
    html = read("dev.html")
    html = html.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + read("styles.css") + "</style>")
    html = html.replace('<script type="module" src="src/main.js"></script>', "<script>\n" + js + "</script>")
    html = html.replace("<!-- Phaser (game engine), then the game itself as ES modules. -->", "<!-- Built by build.py from dev.html: edit the source files, not this one. -->")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"Built index.html ({len(modules)} modules, {len(html) // 1024} KB)")


if __name__ == "__main__":
    build()
