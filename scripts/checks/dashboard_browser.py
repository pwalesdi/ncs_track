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
  - Spot use: every donut caption's counts sum to its total, and the legend swatches are the
    colors the donuts draw
  - definition popovers: every info button on every tab opens its popover on click / tap, the
    popover stays inside the screen, and Esc closes it and returns focus; at 1400 px they open on
    hover and close when the mouse leaves; at 390 px (touch) a tap outside closes them; keyboard
    (focus + Enter) opens them; Compare shows the selected metric's "What it counts" line
Screenshots: outputs/tabs/{width}_{tab}.png (default view), {width}_{tab}_{mode}.png (2026, pooled),
{width}_{tab}_{scenario}.png (every tab under each alternative allocation) and
{width}_compare_{metric}.png (every metric of the Compare scenarios tab) and
{width}_compare_popover.png (Compare tab with a definition popover open).
Exit 1 on any failure.
"""

import sys

from playwright.sync_api import sync_playwright

from ncs_track import paths

HTML = paths.ROOT / "dashboard" / "index.html"
SHOTS = paths.OUTPUTS / "tabs"
WIDTHS = (390, 1400)
TABS = ["overview", "compare", "curve", "makeup", "spots", "perf", "use", "left", "defs"]
SCENARIOS = ["a_5553", "b_4443", "c_3333"]
METRICS = ["flo_in", "flo_out", "added", "removed", "removed_final", "gain", "merit", "share"]
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
  const captions = [...panel.querySelectorAll('[data-parts]')].map(e => {
    const total = Number(e.dataset.total), parts = e.dataset.parts.split(',').map(Number);
    const m = e.textContent.split(': ')[1] || '';
    const shown = m ? m.split(' · ').map(t => parseInt(t, 10)) : [];
    return {total, partsSum: parts.reduce((a, b) => a + b, 0), shownSum: shown.reduce((a, b) => a + b, 0),
            text: e.textContent};
  });
  const badCaptions = captions.filter(c => c.partsSum !== c.total || (c.total > 0 && c.shownSum !== c.total));
  const swatch = [...panel.querySelectorAll('#lg-use span')].map(e => e.style.getPropertyValue('--c').trim().toLowerCase());
  const norm = c => { const x = document.createElement('i'); x.style.color = c; document.body.appendChild(x);
                      const r = getComputedStyle(x).color; x.remove(); return r; };
  const legendMismatch = [];
  if (swatch.length) {
    panel.querySelectorAll('canvas').forEach(c => {
      const ch = Chart.getChart(c); if (!ch || ch.config.type !== 'doughnut') return;
      const drawn = ch.data.datasets[0].backgroundColor.map(norm), want = swatch.map(norm);
      if (JSON.stringify(drawn) !== JSON.stringify(want)) legendMismatch.push(c.id);
    });
  }
  const text = document.body.innerText;
  const badText = /\\bundefined\\b|\\bNaN\\b/.test(text);
  const badLabels = strings.filter(s => /\\bundefined\\b|\\bNaN\\b/.test(s));
  return {scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, charts, badText, badLabels: badLabels.slice(0, 5),
          nCharts: canvases.length, nCaptions: captions.length, badCaptions: badCaptions.slice(0, 3),
          legendMismatch};
}"""

CARDS_JS = """() => {
  const out = {sixth: {}, depth: null, tv_spots: null, noshow: null};
  document.querySelectorAll('[data-head="sixth"]').forEach(el => {
    out.sixth[el.dataset.area] = [Number(el.dataset.entries), Number(el.dataset.median)]; });
  const d = document.getElementById('card-depth').dataset;
  out.depth = {tv: [Number(d.tvEntries), Number(d.tvMedian)], others: [Number(d.otEntries), Number(d.otMedian)]};
  const tv = document.getElementById('card-tv'), un = document.getElementById('card-noshow');
  out.tv_spots = [Number(tv.dataset.k), Number(tv.dataset.n)];
  out.noshow = [Number(un.dataset.k), Number(un.dataset.n)];
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
    if s["badCaptions"]:
        problems.append(f"{label}: donut captions don't sum to their totals: {s['badCaptions']}")
    if s["legendMismatch"]:
        problems.append(f"{label}: legend colors differ from the drawn donut colors: {s['legendMismatch']}")
    return problems, s


def check_headline(page, label: str) -> list[str]:
    sys.path.insert(0, str(paths.ROOT / "tests"))
    from test_dashboard import expected_headline
    got, want = page.evaluate(CARDS_JS), expected_headline()
    problems = []
    for a, v in want["sixth"].items():
        if tuple(got["sixth"].get(a, [])) != tuple(v):
            problems.append(f"{label}: 6th-place card {a} shows {got['sixth'].get(a)}, tables give {v}")
    for k, v in want["depth"].items():
        if tuple(got["depth"][k]) != tuple(v):
            problems.append(f"{label}: depth card {k} shows {got['depth'][k]}, tables give {v}")
    for k in ("tv_spots", "noshow"):
        if tuple(got[k]) != tuple(want[k]):
            problems.append(f"{label}: card {k} shows {got[k]}, tables give {want[k]}")
    return problems


POP_JS = """() => {
  const p = document.getElementById('pop'), r = p.getBoundingClientRect(), vw = document.documentElement.clientWidth;
  return {open: p.classList.contains('open'), left: r.left, right: r.right, top: r.top, bottom: r.bottom, vw, vh: innerHeight,
          title: (p.querySelector('h4') || {}).textContent || '', text: p.innerText,
          focusTerm: (document.activeElement && document.activeElement.dataset) ? document.activeElement.dataset.term || '' : '',
          scrollWidth: document.documentElement.scrollWidth};
}"""


def pop_state(page) -> dict:
    return page.evaluate(POP_JS)


def pop_problems(st: dict, label: str, want_open: bool = True) -> list[str]:
    out = []
    if st["open"] != want_open:
        out.append(f"{label}: popover {'not open' if want_open else 'still open'}")
    if want_open and st["open"]:
        if st["left"] < 0 or st["right"] > st["vw"] or st["top"] < 0 or st["bottom"] > st["vh"]:
            out.append(f"{label}: popover off screen {st}")
        if not st["title"] or "undefined" in st["text"] or "NaN" in st["text"]:
            out.append(f"{label}: popover text bad: {st['text'][:80]!r}")
    if st["scrollWidth"] > st["vw"] + 1:
        out.append(f"{label}: page scrolls horizontally with popover ({st['scrollWidth']} > {st['vw']})")
    return out


def check_popovers(page, width: int, tab: str) -> list[str]:
    """Open every info button in the active tab (click / tap), check it, close with Esc."""
    problems = []
    buttons = page.locator(".tabpanel.active button.info")
    n = buttons.count()
    for i in range(n):
        b = buttons.nth(i)
        if not b.is_visible():
            continue
        term = b.get_attribute("data-term")
        b.scroll_into_view_if_needed()
        if width < 700:
            b.tap()
        else:
            b.click()
        page.wait_for_timeout(60)
        label = f"{width}px {tab} info[{term}]"
        st = pop_state(page)
        problems += pop_problems(st, label)
        page.keyboard.press("Escape")
        page.wait_for_timeout(40)
        st = pop_state(page)
        problems += pop_problems(st, label + " after Esc", want_open=False)
        if st["focusTerm"] != term:
            problems.append(f"{label}: Esc didn't return focus to the info button")
    return problems


def check_compare_popover(page, width: int) -> list[str]:
    """Compare tab: the 'What it counts' line, hover / tap / outside / keyboard behaviour, screenshot."""
    problems = []
    goto_tab(page, "compare")
    page.click('#metric .mbtn[data-v="merit"]')
    page.wait_for_timeout(150)
    what = page.inner_text("#metric-what")
    if "What it counts:" not in what or "24 best Area-meet marks" not in what:
        problems.append(f"{width}px compare: 'What it counts' line wrong: {what[:80]!r}")
    chip_info = page.locator('#metric .mchip[data-v="merit"] button.info')
    if width >= 700:
        chip_info.hover()
        page.wait_for_timeout(120)
        problems += pop_problems(pop_state(page), f"{width}px compare hover")
        page.mouse.move(5, 5)
        page.wait_for_timeout(400)
        problems += pop_problems(pop_state(page), f"{width}px compare mouse left", want_open=False)
        chip_info.hover()                                   # open again for the screenshot
        page.wait_for_timeout(150)
    else:
        chip_info.scroll_into_view_if_needed()
        chip_info.tap()
        page.wait_for_timeout(120)
        problems += pop_problems(pop_state(page), f"{width}px compare tap")
        page.touchscreen.tap(width // 2, 860 - 20)          # tap outside (bottom of screen)
        page.wait_for_timeout(120)
        problems += pop_problems(pop_state(page), f"{width}px compare tap outside", want_open=False)
        chip_info.tap()
        page.wait_for_timeout(150)
    st = pop_state(page)
    problems += pop_problems(st, f"{width}px compare popover for screenshot")
    if "Better =" not in st["text"] or "Example:" not in st["text"]:
        problems.append(f"{width}px compare popover misses Example / Better: {st['text'][:120]!r}")
    page.screenshot(path=str(SHOTS / f"{width}_compare_popover.png"))
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)
    # keyboard: focus an info button, Enter opens, Esc closes
    page.locator('#metric .mchip[data-v="added"] button.info').focus()
    page.keyboard.press("Enter")
    page.wait_for_timeout(80)
    st = pop_state(page)
    problems += pop_problems(st, f"{width}px compare keyboard Enter")
    if "gain a spot" not in st["title"]:
        problems.append(f"{width}px compare keyboard: wrong popover {st['title']!r}")
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)
    problems += pop_problems(pop_state(page), f"{width}px compare keyboard Esc", want_open=False)
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


def set_scenario(page, width: int, value: str):
    if width < 700:
        page.click("#fbtn")
    page.click(f'#scenario button[data-v="{value}"]')
    if width < 700:
        page.click("#fbtn")
    page.wait_for_timeout(150)


def run() -> dict:
    SHOTS.mkdir(parents=True, exist_ok=True)
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            touch = width < 700
            page = browser.new_page(viewport={"width": width, "height": 900 if width > 700 else 844}, has_touch=touch, is_mobile=touch)
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
                if tab == "use":
                    charts_seen["use_captions_checked"] = s["nCaptions"]
                page.screenshot(path=str(SHOTS / f"{width}_{tab}.png"), full_page=True)
                pops = check_popovers(page, width, tab)
                problems += pops
                charts_seen[f"{tab}_info_buttons"] = page.locator(".tabpanel.active button.info").count()
            for mode, value in MODES.items():
                set_season(page, width, value)
                for tab in ("curve", "makeup", "spots", "perf", "use", "left"):
                    goto_tab(page, tab)
                    pr, s = check(page, f"{width}px {tab} {mode}")
                    problems += pr
                    charts_seen[f"{tab}_{mode}"] = s["nCharts"]
                    if tab == "use":
                        charts_seen[f"use_{mode}_captions_checked"] = s["nCaptions"]
                    page.screenshot(path=str(SHOTS / f"{width}_{tab}_{mode}.png"), full_page=True)
            set_season(page, width, "side")
            for scen in SCENARIOS:                     # every tab under every alternative allocation
                set_scenario(page, width, scen)
                for tab in TABS:
                    goto_tab(page, tab)
                    pr, s = check(page, f"{width}px {tab} {scen}")
                    problems += pr
                    charts_seen[f"{tab}_{scen}"] = s["nCharts"]
                    page.screenshot(path=str(SHOTS / f"{width}_{tab}_{scen}.png"), full_page=True)
            set_scenario(page, width, "current")
            goto_tab(page, "compare")
            for m in METRICS:                          # every metric of the Compare tab
                page.click(f'#metric .mbtn[data-v="{m}"]')
                page.wait_for_timeout(150)
                pr, s = check(page, f"{width}px compare {m}")
                problems += pr
                charts_seen[f"compare_{m}"] = s["nCharts"]
                page.screenshot(path=str(SHOTS / f"{width}_compare_{m}.png"), full_page=True)
            problems += check_compare_popover(page, width)
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
