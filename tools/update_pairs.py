#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
pairs = ["BTC-USD","BCH-USD","BSV-USD","LTC-USD","DGB-USD","ETH-USD","ETC-USD","OP-USD","ARB-USD","MATIC-USD"]
def update_config():
    p=ROOT/"src"/"config.py"
    if not p.exists(): print("✖ config.py not found"); return
    t=p.read_text(encoding="utf-8").splitlines(); out=[]; inside=False
    for line in t:
        if line.strip().startswith("DEFAULT_SYMBOLS"):
            inside=True; out.append("DEFAULT_SYMBOLS = ["); 
            for s in pairs: out.append(f'    "{s}",')
            out[-1]=out[-1].rstrip(","); out.append("]")
        elif inside and line.strip().startswith("]"):
            inside=False
        elif not inside:
            out.append(line)
    p.write_text("\n".join(out),encoding="utf-8"); print("✔ config.py updated")
def update_sample():
    (ROOT/"sample_symbols.txt").write_text("\n".join(pairs)+"\n",encoding="utf-8")
    print("✔ sample_symbols.txt updated")
if __name__=="__main__":
    update_config(); update_sample()
    print("✨ Pairs updated successfully!")
