"""Build dist/deep-schema.html: one file you can publish or open directly.

The source in src/ uses JavaScript modules (import/export). Browsers only load
modules from a web server, so this script bundles them into a single script:
it follows the imports from src/main.js, orders the modules so each one runs
after the modules it imports, and wraps each in its own scope.
No Node.js needed, just Python 3.

Usage:  python build.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent
SRC = ROOT / "src"
ENTRY = SRC / "main.js"

IMPORT_RE = re.compile(r'^\s*import\s*\{([^}]*)\}\s*from\s*"([^"]+)";?\s*$', re.M)
IMPORT_NS_RE = re.compile(r'^\s*import\s*\*\s*as\s+(\w+)\s+from\s*"([^"]+)";?\s*$', re.M)
EXPORT_RE = re.compile(r'^export\s+(?:async\s+)?(const|let|function|class)\s+([A-Za-z_$][\w$]*)', re.M)

modules = {}   # path -> {"code": str, "deps": [path], "exports": [name]}
order = []

def resolve(base: Path, spec: str) -> Path:
    return (base.parent / spec).resolve()

def visit(path: Path, stack=()):
    if path in modules:
        return
    if path in stack:
        chain = " -> ".join(p.name for p in stack + (path,))
        raise SystemExit(f"Circular import: {chain}")
    code = path.read_text(encoding="utf-8")
    deps = [resolve(path, m.group(2)) for m in IMPORT_RE.finditer(code)] + [resolve(path, m.group(2)) for m in IMPORT_NS_RE.finditer(code)]
    for d in deps:
        visit(d, stack + (path,))
    exports = [m.group(2) for m in EXPORT_RE.finditer(code)]
    for m in EXPORT_RE.finditer(code):
        if m.group(1) == "let":
            raise SystemExit(f"{path.name}: 'export let {m.group(2)}' is not supported; export a const object instead")
    modules[path] = {"code": code, "deps": deps, "exports": exports}
    order.append(path)

def key(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()

def convert(path: Path) -> str:
    info = modules[path]
    code = info["code"]
    def imp(m):
        names, spec = m.group(1), m.group(2)
        parts = []
        for n in names.split(","):
            n = n.strip()
            if not n:
                continue
            if " as " in n:
                a, b = [x.strip() for x in n.split(" as ")]
                parts.append(f"{a}: {b}")
            else:
                parts.append(n)
        return f'const {{ {", ".join(parts)} }} = __mods["{key(resolve(path, spec))}"];'
    code = IMPORT_RE.sub(imp, code)
    code = IMPORT_NS_RE.sub(lambda m: f'const {m.group(1)} = __mods["{key(resolve(path, m.group(2)))}"];', code)
    code = re.sub(r'^export\s+(?=(?:async\s+)?(?:const|function|class)\b)', "", code, flags=re.M)
    ret = ", ".join(info["exports"])
    return f'/* ===== {key(path)} ===== */\n__mods["{key(path)}"] = (() => {{\n{code}\nreturn {{ {ret} }};\n}})();\n'

visit(ENTRY.resolve())
bundle = "(() => {\n\"use strict\";\nconst __mods = {};\n" + "\n".join(convert(p) for p in order) + "})();\n"

html = (SRC / "index.html").read_text(encoding="utf-8")
css = (SRC / "styles.css").read_text(encoding="utf-8")
# Keep the whole page (including the startup check in <head>); inline the CSS and the bundled modules.
out = html.replace('<link rel="stylesheet" href="styles.css">', "<style>\n" + css + "</style>", 1)
out = out.replace('<script type="module" src="main.js"></script>', "<script>\n" + bundle + "</script>", 1)
(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist" / "deep-schema.html").write_text(out, encoding="utf-8")
print(f"Built dist/deep-schema.html from {len(order)} modules ({len(out) // 1024} KB)")
