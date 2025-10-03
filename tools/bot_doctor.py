#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
GREEN="\033[92m"; RED="\033[91m"; YELLOW="\033[93m"; BOLD="\033[1m"; RESET="\033[0m"
ok=lambda m: print(f"{GREEN}✔ {m}{RESET}")
fail=lambda m: print(f"{RED}✖ {m}{RESET}")
warn=lambda m: print(f"{YELLOW}• {m}{RESET}")
def run(cmd): 
    print(f"{YELLOW}$ {' '.join(cmd)}{RESET}")
    return subprocess.call(cmd)==0
def check_files():
    top=["README.md","requirements.txt","sample_symbols.txt","src"]
    src=["main.py","signals.py","analysis.py","data_sources.py","telegram_bot.py","config.py"]
    good=True
    for f in top:
        p=ROOT/f; (ok if p.exists() else fail)(f"top: {f} {'found' if p.exists() else 'missing'}"); good&=p.exists()
    for f in src:
        p=ROOT/'src'/f; (ok if p.exists() else fail)(f"src: {f} {'found' if p.exists() else 'missing'}"); good&=p.exists()
    return good
def check_deps():
    try: out=subprocess.check_output([sys.executable,"-m","pip","list"],text=True).lower()
    except Exception as e: fail(f"pip list failed: {e}"); return False
    need=["pandas","numpy","yfinance","ta","nltk"]; miss=[p for p in need if p not in out]
    if miss: fail("missing deps: "+", ".join(miss)); return False
    ok("core deps installed"); return True
def test_imports():
    try: import pandas, numpy, yfinance, ta, nltk  # noqa
    except Exception as e: fail(f"import error: {e}"); return False
    ok("imports OK"); return True
def dry_run_online():
    return run([sys.executable,"-m","src.main","--symbols","BTC-USD,ETH-USD","--once","--no-telegram"])
def ensure_pip():
    if not run([sys.executable,"-m","pip","--version"]):
        warn("pip missing → bootstrapping ensurepip")
        if not run([sys.executable,"-m","ensurepip","--upgrade"]): fail("ensurepip failed"); return False
    run([sys.executable,"-m","pip","install","--upgrade","pip","setuptools","wheel"]); ok("pip ready"); return True
def install_requirements():
    req=ROOT/"requirements.txt"
    if not req.exists(): fail("requirements.txt missing"); return False
    return run([sys.executable,"-m","pip","install","-r",str(req)])
def ensure_vader():
    run([sys.executable,"-m","nltk.downloader","vader_lexicon"]); return True
def main():
    do_fix="--fix" in sys.argv; online="--online" in sys.argv
    print(f"{BOLD}Bot Doctor — Market Alert Bot{RESET}\n")
    healthy = check_files() & check_deps() & test_imports()
    if online:
        if dry_run_online(): ok("online dry-run OK")
        else: warn("online dry-run failed; continue…")
    if not do_fix: sys.exit(0 if healthy else 1)
    print(f"\n{BOLD}Running Quick Fix…{RESET}")
    all_ok = ensure_pip() & install_requirements() & ensure_vader() & test_imports()
    if online: all_ok &= dry_run_online()
    sys.exit(0 if all_ok else 1)
if __name__=="__main__": main()
