#!/usr/bin/env python3
"""Patch static/js/app.js for server-backed APP_DATA."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "static" / "js" / "app.js"


def main() -> None:
    text = JS.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    replaced_app_data = False
    while i < len(lines):
        line = lines[i]
        if line.startswith("const APP_DATA = ") and not replaced_app_data:
            out.append(
                "let APP_DATA = { sold:[], stock:[], investors:[], monthly:[], expenses:[], collections:[], money_in:[], money_out:[] };\n"
            )
            replaced_app_data = True
            i += 1
            continue
        out.append(line)
        i += 1
    text = "".join(out)

    marker = "let stockData = APP_DATA.stock.map(v => Object.assign({}, v));"
    if marker not in text:
        raise SystemExit("patch: stockData marker not found")

    insert = """let stockData = [];
let collections = [];
function hydrateFromAppData() {
  stockData = (APP_DATA.stock || []).map(v => Object.assign({}, v));
  collections = (APP_DATA.collections || []).map(v => Object.assign({}, v));
  finLog = [];
  (APP_DATA.expenses || []).forEach((e, i) => {
    const notePlate = ((e.notes||'') + ' ' + (e.from||'')).match(/[A-Z]{2}\\d{2}\\s?[A-Z]{3}/i);
    const plate = notePlate ? notePlate[0].replace(/\\s+/g,' ').trim().toUpperCase() : '';
    const vehicle = plate ? stockData.find(v=>normP(v.plate)===normP(plate)) || (APP_DATA.sold||[]).find(v=>normP(v.plate)===normP(plate)) : null;
    finLog.push({id:'h'+i, date:(e.month||'').slice(0,10), plate: plate, model: vehicle ? vehicle.model : '', desc:[(e.from||''),(e.notes||e.category||'')].filter(Boolean).join(' · '), cat:e.category||'Other', amount:e.amount||0, direction:'out'});
  });
  (APP_DATA.money_in||[]).forEach((e,i)=>{
    const vehicle = e.plate ? stockData.find(v=>normP(v.plate)===normP(e.plate)) || (APP_DATA.sold||[]).find(v=>normP(v.plate)===normP(e.plate)) : null;
    finLog.push({id:'mi'+i,date:e.date||e.month,plate:e.plate||'',model:vehicle?vehicle.model:'',desc:(e.category||'Money In')+(e.notes?' · '+e.notes:''),cat:'Money In',amount:-(e.amount||0),direction:'in'});
  });
  (APP_DATA.money_out||[]).forEach((e,i)=>{
    finLog.push({id:'mo'+i,date:e.date||e.month,plate:'',model:'',desc:(e.category||'Money Out')+(e.notes?' · '+e.notes:''),cat:'Money Out',amount:e.amount||0,direction:'out'});
  });
}
"""
    text = text.replace(
        "let stockData = APP_DATA.stock.map(v => Object.assign({}, v));\nlet finLog = [];\nlet viewings =",
        insert + "let viewings =",
    )

    old_coll = "let collections = (APP_DATA.collections||[]).map(v => Object.assign({}, v));\n"
    if old_coll in text:
        text = text.replace(old_coll, "")

    dom_old = """document.addEventListener('DOMContentLoaded', function() {
  // Set logo everywhere
  document.getElementById('sidebar-logo').src = LOGO;
  document.getElementById('dash-logo').src = LOGO;"""
    dom_new = """document.addEventListener('DOMContentLoaded', async function() {
  async function loadAppState() {
    const r = await fetch('/api/app-state');
    if (!r.ok) throw new Error('app-state ' + r.status);
    APP_DATA = await r.json();
    hydrateFromAppData();
  }
  await loadAppState();
  // Set logo everywhere
  const _sl = document.getElementById('sidebar-logo'); if (_sl) _sl.src = LOGO;
  const _dl = document.getElementById('dash-logo'); if (_dl) _dl.src = LOGO;"""
    if dom_old not in text:
        raise SystemExit("patch: DOMContentLoaded block not found")
    text = text.replace(dom_old, dom_new)

    JS.write_text(text, encoding="utf-8")
    print("patched", JS)


if __name__ == "__main__":
    main()
