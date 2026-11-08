"""ดึงผล Magnum 4D (รางวัลที่ 1-3) งวดใหม่จาก deadboy18/malaysia-4d แล้วต่อท้าย data4d.js
- เพิ่มเฉพาะงวดที่วันที่ใหม่กว่างวดล่าสุด ไม่แก้งวดเก่า
- เลขต้องเป็นตัวเลข 4 หลัก (เติม 0 ข้างหน้า)
"""
import csv, io, json, re, sys, urllib.request
from datetime import datetime, timezone, timedelta

import os
SRC = os.environ.get("SRC_CSV") or "https://raw.githubusercontent.com/deadboy18/malaysia-4d/main/data/magnum_draws.csv"
PATH = "data4d.js"

raw = open(PATH, encoding="utf-8").read()
m = re.match(r"\s*window\.TLA_MY\s*=\s*(\{.*\})\s*;\s*$", raw, re.S)
if not m:
    sys.exit("data4d.js format not recognised")
data = json.loads(m.group(1))
last = data["draws"][-1][0]

if SRC.startswith("http"):
    with urllib.request.urlopen(SRC, timeout=60) as r:
        text = r.read().decode("utf-8")
else:
    text = open(SRC, encoding="utf-8").read()
rows = list(csv.DictReader(io.StringIO(text)))

new = []
for r in rows:
    d = (r.get("date") or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or d <= last:
        continue
    nums = [(r.get(k) or "").strip() for k in ("prize_1", "prize_2", "prize_3")]
    if not all(re.fullmatch(r"\d{1,4}", n) for n in nums):
        print("skip bad row", d, nums); continue
    new.append([d] + [n.zfill(4) for n in nums])
new.sort()
seen = set()
new = [x for x in new if not (x[0] in seen or seen.add(x[0]))]

if not new:
    print("no new draws after", last); sys.exit(0)

data["draws"].extend(new)
now = datetime.now(timezone(timedelta(hours=7)))
data["updated"] = now.isoformat(timespec="seconds")
data["log"].append(f"{now:%Y-%m-%d} GitHub Actions เพิ่ม {len(new)} งวด: " + ", ".join(x[0] for x in new))
open(PATH, "w", encoding="utf-8").write("window.TLA_MY = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("added", new)
