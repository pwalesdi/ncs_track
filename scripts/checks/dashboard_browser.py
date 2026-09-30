"""Browser check of dashboard/index.html with Playwright (headless Chromium).

    .venv/bin/python scripts/checks/dashboard_browser.py

At 390 px and 1400 px wide, with every network request blocked (the page must work offline),
for every tab, in the default "all seasons side by side" view and again focused on 2026 and
pooled:
  - no console errors or page errors
  - no page-level horizontal scroll
  - every chart in the visible tab exists and has drawn data
  - no "undefined" or "NaN" in the page text or in any chart label, tooltip text or centre text
  - the Overview cards show the numbers pandas computes from data/summary/
  - below 700 px the filters are behind the "Filters" button
Screenshots: outputs/tabs/{width}_{tab}.png (default view) and {width}_{tab}_{mode}.png.
Exit 1 on any failure.
"""

import sys

from playwright.sync_api import sync_playwright

from ncs_track import paths

HTML = paths.ROOT / "dashboard" / "index.html"
SHOTS = paths.OUTPUTS / "tabs"
WIDTHS = (390, 1400)
TABS = ["overview", "curve", "makeup", "spots", "perf", "use", "left", "defs"]
MODES = {"2026": "2026", "pooled": "all"}

STATE_JS = """() => {
  const doc = document.documentElement;
  const panel = document.querySelector('.tabpanel.active');
  const canvases = [...panel.querySelectorAll('canvas')];
  const charts = canvases.map(c => {
    const ch = Chart.getChart(c);
    const ok = !!ch && ch.data.datasets.length > 0 && c.width > 0 && c.height > 0 &&
               ch.data.datasets.some(d => (d.data || []).some(v => v !== null && v !== undefined && (typeof v !== 'object' || v.y !== null)));
    return {id: c.id, ok};
  });
  const strings = [];
  Object.values(Chart.instances).forEach(ch => {
    ch.data.datasets.forEach(d => {
      strings.push(String(d.label));
      ['endLabels', 'segLabels', 'tips'].forEach(k => (d[k] || []).forEach(s => strings.push(String(s))));
      (d.data || []).forEach(v => { if (v && typeof v === 'object' && v.cell) strings.push(JSON.stringify(v.cell)); });
    });
    const p = ch.options.plugins || {};
    ((p.valueLabels || {}).totals || []).forEach(s => strings.push(String(s)));
    if (p.centerText && p.centerText.big !== undefined) strings.push(String(p.centerText.big));
  });
  const text = document.body.innerText;
  const badText = /\\bundefined\\b|\\bNaN\\b/.test(text);
  const badLabels = strings.filter(s => /\\bundefined\\b|\\bNaN\\b/.test(s));
  return {scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, charts, badText, badLabels: badLabels.slice(0, 5),
          nCharts: canvases.length};
}"""

CARDS_JS = """() => {
  const out = {finish: {}, tv_spots: null, unfilled: null};
  document.querySelectorAll('[data-head="finish"]').forEach(el => {
    out.finish[el.dataset.area] = [Number(el.dataset.entries), Number(el.dataset.median)]; });
  const tv = document.getElementById('card-tv'), un = document.getElementById('card-unfilled');
  out.tv_spots = [Number(tv.dataset.k), Number(tv.dataset.n)];
  out.unfilled = [Number(un.dataset.k), Number(un.dataset.n)];
  return out;
}"""


def check(page, label: str) -> tuple[list[str], dict]:
    s = page.evaluate(STATE_JS)
    problems = []
    if s["scrollWidth"] > s["clientWidth"] + 1:
        problems.append(f"{label}: page scrolls horizontally ({s['scrollWidth']} > {s['clientWidth']})")
    bad = [c["id"] for c in s["charts"] if not c["ok"]]
    if bad:
        problems.append(f"{label}: charts not rendered: {bad}")
    if s["badText"]:
        problems.append(f"{label}: 'undefined' or 'NaN' in page text")
    if s["badLabels"]:
        problems.append(f"{label}: 'undefined' or 'NaN' in chart labels: {s['badLabels']}")
    return problems, s


def check_headline(page, label: str) -> list[str]:
    sys.path.insert(0, str(paths.ROOT / "tests"))
    from test_dashboard import expected_headline
    got, want = page.evaluate(CARDS_JS), expected_headline()
    problems = []
    for a, v in want["finish"].items():
        if tuple(got["finish"].get(a, [])) != tuple(v):
            problems.append(f"{label}: finish card {a} shows {got['finish'].get(a)}, tables give {v}")
    for k in ("tv_spots", "unfilled"):
        if tuple(got[k]) != tuple(want[k]):
            problems.append(f"{label}: card {k} shows {got[k]}, tables give {want[k]}")
    return problems


def goto_tab(page, tab: str):
    page.click(f'#tabs button[data-tab="{tab}"]')
    page.wait_for_timeout(150)


def set_season(page, width: int, value: str):
    if width < 700:
        page.click("#fbtn")
    page.select_option("#season", value)
    if width < 700:
        page.click("#fbtn")
    page.wait_for_timeout(150)


def run() -> dict:
    SHOTS.mkdir(parents=True, exist_ok=True)
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            page = browser.new_page(viewport={"width": width, "height": 900 if width > 700 else 844})
            errors, requests = [], []
            page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:")
                       else (requests.append(route.request.url), route.abort()))
            page.goto(HTML.as_uri())
            page.wait_for_timeout(400)
            problems = check_headline(page, f"{width}px")
            if width < 700:
                hidden = page.evaluate("getComputedStyle(document.getElementById('filters')).display") == "none"
                if not hidden:
                    problems.append(f"{width}px: filters not collapsed behind the Filters button")
                page.click("#fbtn")
                pr, _ = check(page, f"{width}px filters open")
                problems += pr
                page.click("#fbtn")
            charts_seen = {}
            for tab in TABS:
                goto_tab(page, tab)
                pr, s = check(page, f"{width}px {tab}")
                problems += pr
                charts_seen[tab] = s["nCharts"]
                page.screenshot(path=str(SHOTS / f"{width}_{tab}.png"), full_page=True)
            for mode, value in MODES.items():
                set_season(page, width, value)
                for tab in ("curve", "makeup", "spots", "perf", "use", "left"):
                    goto_tab(page, tab)
                    pr, s = check(page, f"{width}px {tab} {mode}")
                    problems += pr
                    charts_seen[f"{tab}_{mode}"] = s["nCharts"]
                    page.screenshot(path=str(SHOTS / f"{width}_{tab}_{mode}.png"), full_page=True)
            set_season(page, width, "side")
            results[width] = {"problems": problems + errors, "blocked_network_requests": requests, "charts": charts_seen}
            page.close()
        browser.close()
    return results


def main() -> int:
    results = run()
    fail = False
    for width, r in results.items():
        print(f"{width}px: problems {len(r['problems'])}; network requests attempted {len(r['blocked_network_requests'])}")
        print("   charts per tab/mode:", r["charts"])
        for pr in r["problems"]:
            print("  ", pr)
        fail |= bool(r["problems"]) or bool(r["blocked_network_requests"])
    print(f"screenshots: {SHOTS.relative_to(paths.ROOT)}/<width>_<tab>[_<mode>].png")
    print("FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
