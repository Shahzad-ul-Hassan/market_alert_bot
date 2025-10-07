import os, re, sys, shutil, time, traceback, py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC  = ROOT / "src"
BACK = ROOT / f".backup_src_{int(time.time())}"

print(f"🩺 Project Doctor\nROOT={ROOT}\nSRC={SRC}\nBACKUP={BACK}")

if not SRC.exists():
    print("❌ src folder not found."); sys.exit(1)

# 0) full backup
if not BACK.exists():
    shutil.copytree(SRC, BACK)
    print(f"✅ Backup created at {BACK}")

# helpers
def sanitize_text(txt: str) -> str:
    # A) strip any prelude until first valid python token
    txt = re.sub(r'^[\s\S]*?(?=^\s*(from|import|def|class|#|"""|\'\'\'|@))','',txt, flags=re.M)
    # B) remove heredoc/cat artifacts & code fences
    txt = re.sub(r'(?m)^\s*cat\s+>>?.*$', '', txt)
    txt = re.sub(r'(?m)^.*<<\s*([\'"]?)(PY|BASH|EOF)\1\s*$', '', txt)
    txt = re.sub(r'(?m)^\s*(PY|BASH|EOF)\s*$', '', txt)
    txt = re.sub(r'(?m)^\s*```.*$', '', txt)
    # C) remove explicit shell error echoes (e.g., "bash: line 1: ...")
    txt = re.sub(r'(?m)^\s*bash:\s.*$', '', txt)
    # D) normalize fancy quotes
    txt = txt.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    # E) collapse extra blank lines
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    return txt.strip() + "\n"

def dedupe_functions(txt: str) -> str:
    # keep first def block of any name, drop subsequent same-name blocks
    out = []
    seen = set()
    lines = txt.splitlines(keepends=False)
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', line)
        if m:
            name = m.group(1)
            # capture this def block until next top-level def/class or EOF
            j = i + 1
            while j < len(lines) and not re.match(r'^(def|class)\s+', lines[j]):
                j += 1
            block = lines[i:j]
            if name in seen:
                # drop duplicate
                pass
            else:
                seen.add(name)
                out.extend(block)
            i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out) + ("\n" if not out or out[-1] != "" else "")

def normalize_imports(txt: str) -> str:
    # src.module → relative imports
    txt = re.sub(r'(?m)^from\s+src\.([a-zA-Z_][\w]*)\s+import\s+', r'from .\1 import ', txt)
    txt = re.sub(r'(?m)^import\s+src\.([a-zA-Z_][\w]*)\s+as\s+([a-zA-Z_][\w]*)\s*$', r'from . import \1 as \2', txt)
    txt = re.sub(r'(?m)^import\s+src\.([a-zA-Z_][\w]*)\s*$', r'from . import \1', txt)
    return txt

def process_file(p: Path):
    raw = p.read_text(encoding='utf-8', errors='ignore')
    s1 = sanitize_text(raw)
    s2 = normalize_imports(s1)
    s3 = dedupe_functions(s2)
    if s3 != raw:
        p.write_text(s3, encoding='utf-8')
        return True
    return False

changed = 0
for py in sorted(SRC.glob("*.py")):
    if py.name == "__init__.py": 
        continue
    try:
        if process_file(py): 
            print(f"🧹 Cleaned: {py.name}")
            changed += 1
    except Exception as e:
        print(f"⚠️ Could not clean {py.name}: {e}")

# compile check & contextual errors
print("\n🧪 Compile check:")
ok = True
for py in sorted(SRC.glob("*.py")):
    try:
        py_compile.compile(str(py), doraise=True)
        print(f"  ✅ {py.name}")
    except Exception as e:
        ok = False
        print(f"  ❌ {py.name} → {e}")
        # show 15 lines around failing line if possible
        try:
            import traceback
            tb = traceback.TracebackException.from_exception(e)
            # parse message to extract line number (best effort)
            import re
            m = re.search(r'\(.*?, line (\d+)\)', str(e))
            if m:
                ln = int(m.group(1))
                start = max(1, ln-7); end = ln+7
                print(f"----- {py.name} lines {start}-{end} -----")
                with open(py, 'r', encoding='utf-8', errors='ignore') as fh:
                    for idx, line in enumerate(fh, 1):
                        if start <= idx <= end:
                            mark = ">>" if idx == ln else "  "
                            print(f"{mark} {idx:4d}: {line.rstrip()}")
        except Exception:
            pass

print("\n📊 Summary:")
print(f"Files cleaned: {changed}")
print("Status:", "✅ ALL GOOD" if ok else "❌ Fix required")
sys.exit(0 if ok else 2)
