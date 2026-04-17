#!/usr/bin/env /opt/homebrew/bin/python3
"""
generate_dashboard.py
Reads the Push Films accounts spreadsheet and writes dashboard_data.json.

Run after any spreadsheet update, then:
    git add dashboard_data.json && git commit -m "Update dashboard data" && git push
"""

import os, glob, json, re
from datetime import datetime
import openpyxl

# ── Paths ──────────────────────────────────────────────────────────────────────
SPREADSHEET_DIR = os.path.expanduser(
    '~/Library/Mobile Documents/com~apple~CloudDocs/'
    'ICLOUD/GREG PERSONAL /PERSONAL FINANCES /CLAUDE VERSION - MARCH 26 /'
)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_OUT    = os.path.join(SCRIPT_DIR, 'dashboard_data.json')

# ── Find most recently modified ACCOUNTS*.xlsx ────────────────────────────────
xlsx_files = glob.glob(os.path.join(SPREADSHEET_DIR, 'ACCOUNTS*.xlsx'))
if not xlsx_files:
    raise FileNotFoundError(f"No ACCOUNTS*.xlsx found in:\n  {SPREADSHEET_DIR}")
spreadsheet_path = max(xlsx_files, key=os.path.getmtime)
print(f"Reading: {os.path.basename(spreadsheet_path)}")

# ── Load existing JSON — preserve manually annotated fields ───────────────────
existing_atl = {}
if os.path.exists(JSON_OUT):
    with open(JSON_OUT, 'r') as f:
        old = json.load(f)
    for entry in old.get('atl', []):
        existing_atl[entry['m']] = entry

# ── Load workbook (data_only reads cached formula values) ─────────────────────
wb = openpyxl.load_workbook(spreadsheet_path, data_only=True)

# ── Helper: find income column in a monthly tab ───────────────────────────────
def norm(t):
    return re.sub(r'\s+', ' ', str(t or '').lower()).strip()

def find_income_col(ws):
    """Scan row 3 for a header containing 'income' or 'funds in'."""
    for keyword in ['income', 'funds in', 'push income', 'turnover']:
        for col in range(1, min(ws.max_column + 1, 20)):
            if keyword in norm(ws.cell(row=3, column=col).value or ''):
                return col
    return None

# ── Read income from each monthly tab ─────────────────────────────────────────
# Tab names: "PUSH + 108 SEP 2024" etc.  Month label = "SEP 2024"
TAB_RE = re.compile(r'^PUSH \+ \d+ (.+)$')

income_by_month = {}
for sheet_name in wb.sheetnames:
    m = TAB_RE.match(sheet_name)
    if not m:
        continue
    month_label = m.group(1).strip()
    ws = wb[sheet_name]

    income_col = find_income_col(ws)
    if not income_col:
        income_by_month[month_label] = 0.0
        continue

    total = 0.0
    for row in range(4, ws.max_row + 1):
        # Col C (col 3) non-empty = data row; formula/subtotal rows are blank here
        bank_cell = ws.cell(row=row, column=3).value
        if bank_cell is None or bank_cell == '' or bank_cell == 0:
            continue
        val = ws.cell(row=row, column=income_col).value
        if val and isinstance(val, (int, float)) and val > 0:
            total += val

    income_by_month[month_label] = round(total, 2)

# ── Read SUMMARY sheet ────────────────────────────────────────────────────────
ws_sum = wb['SUMMARY']

# Monthly totals — rows 4-22: A=Month B=Spend C=Running D=vs Average
monthly = []
for r in range(4, 23):
    month = ws_sum.cell(row=r, column=1).value
    if not month or str(month).strip() in ('TOTAL', 'MONTHLY AVG', ''):
        continue
    monthly.append({
        'm':       str(month).strip(),
        'spend':   round(float(ws_sum.cell(row=r, column=2).value or 0), 2),
        'running': round(float(ws_sum.cell(row=r, column=3).value or 0), 2),
        'vs':      round(float(ws_sum.cell(row=r, column=4).value or 0), 2),
    })

# Category breakdown — rows 28-46: A=Month C=Food&Drink D=Transport … J=Family
CAT_COLS = {
    'Food & Drink': 3,
    'Transport':    4,
    'Comms':        5,
    'Home':         6,
    'Finance/Work': 7,
    'Lifestyle':    8,
    'Personal':     9,
    'Family':      10,
}
cats = []
for r in range(28, 47):
    month = ws_sum.cell(row=r, column=1).value
    if not month or str(month).strip() in ('TOTAL', 'MONTHLY AVG', ''):
        continue
    entry = {'m': str(month).strip()}
    for cat, col in CAT_COLS.items():
        val = ws_sum.cell(row=r, column=col).value
        entry[cat] = round(float(val or 0), 2)
    cats.append(entry)

# ATL project costs — rows 53-71: A=Month C=Project Costs
atl_costs = {}
for r in range(53, 72):
    month = ws_sum.cell(row=r, column=1).value
    if not month or str(month).strip() in ('TOTAL', ''):
        continue
    costs = ws_sum.cell(row=r, column=3).value or 0
    atl_costs[str(month).strip()] = round(float(costs), 2)

# ── Build ATL array ───────────────────────────────────────────────────────────
# income  → fresh from monthly tabs
# costs   → from SUMMARY col C
# tax, from, breakdown → preserved from existing JSON (manually annotated)
atl = []
for entry in monthly:
    m    = entry['m']
    prev = existing_atl.get(m, {})
    atl.append({
        'm':         m,
        'income':    income_by_month.get(m, 0.0),
        'costs':     atl_costs.get(m, 0.0),
        'tax':       prev.get('tax', 0),
        'from':      prev.get('from', ''),
        'breakdown': prev.get('breakdown', []),
    })

# ── Write JSON ────────────────────────────────────────────────────────────────
out = {
    'generated': datetime.now().isoformat(),
    'source':    os.path.basename(spreadsheet_path),
    'monthly':   monthly,
    'cats':      cats,
    'atl':       atl,
}
with open(JSON_OUT, 'w') as f:
    json.dump(out, f, indent=2)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\nWritten: {JSON_OUT}")
print(f"  {len(monthly)} months · {monthly[0]['m']} – {monthly[-1]['m']}")

if existing_atl:
    changes = []
    for entry in atl:
        old_income = existing_atl.get(entry['m'], {}).get('income')
        if old_income is not None and round(float(old_income), 2) != entry['income']:
            changes.append(f"  {entry['m']}: £{old_income:,.2f} → £{entry['income']:,.2f}")
    if changes:
        print("\nIncome changes vs previous JSON:")
        for c in changes:
            print(c)
    else:
        print("\nNo income changes vs previous JSON.")

print("\nNext step:")
print("  git add dashboard_data.json && git commit -m 'Update dashboard data' && git push")
