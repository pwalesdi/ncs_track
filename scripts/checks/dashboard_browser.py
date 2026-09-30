"""Browser check of dashboard/index.html with Playwright (headless Chromium).

    .venv/bin/python scripts/checks/dashboard_browser.py

At 390 px and 1400 px wide, with every network request blocked (the page must work
offline):
  - no console errors or page errors
  - no page-level horizontal scroll
  - all 6 charts exist and have drawn data
  - the same after changing the filters (declared field, all seasons, girls, throws)
Screenshots go to outputs/dashboard_{width}.png (git-ignored). Exit 1 on any failure.
"""

import json
import sys

from playwright.sync_api import sync_playwright

from ncs_track import paths

HTML = paths.ROOT / "dashboard" / "index.html"
CHARTS = ["c1", "c2", "c3", "c4", "c5", "c6"]
WIDTHS = (390, 1400)

STATE_JS = """() => {
  const doc = document.documentElement;
  const charts = %s.map(id => {
    const c = Chart.getChart(document.getElementById(id));
    return {id, ok: !!c && c.data.datasets.length > 0 && c.data.labels.length > 0
                    && c.canvas.width > 0 && c.canvas.height > 0};
  });
  return {scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, charts};
}""" % json.dumps(CHARTS)


def check(page, label: str) -> list[str]:
    s = page.evaluate(STATE_JS)
    problems = []
    if s["scrollWidth"] > s["clientWidth"] + 1:
        problems.append(f"{label}: page scrolls horizontally ({s['scrollWidth']} > {s['clientWidth']})")
    bad = [c["id"] for c in s["charts"] if not c["ok"]]
    if bad:
        problems.append(f"{label}: charts not rendered: {bad}")
    return problems


def run() -> dict:
    results = {}
    paths.OUTPUTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            page = browser.new_page(viewport={"width": width, "height": 900})
            errors = []
            page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
            requests = []
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:")
                       else (requests.append(route.request.url), route.abort()))
            page.goto(HTML.as_uri())
            page.wait_for_timeout(500)
            problems = check(page, f"{width}px default")
            page.screenshot(path=str(paths.OUTPUTS / f"dashboard_{width}.png"), full_page=True)
            page.click('#field button[data-v="declared"]')
            page.select_option("#season", "all")
            page.select_option("#gender", "girls")
            page.select_option("#event", "group:throws")
            page.wait_for_timeout(300)
            problems += check(page, f"{width}px filtered")
            page.screenshot(path=str(paths.OUTPUTS / f"dashboard_{width}_filtered.png"), full_page=True)
            results[width] = {"problems": problems + errors,
                              "blocked_network_requests": requests,
                              "state": page.evaluate(STATE_JS)}
            page.close()
        browser.close()
    return results


def main() -> int:
    results = run()
    fail = False
    for width, r in results.items():
        s = r["state"]
        drawn = sum(c["ok"] for c in s["charts"])
        print(f"{width}px: scrollWidth {s['scrollWidth']} / clientWidth {s['clientWidth']}; charts drawn {drawn}/6; "
              f"network requests attempted {len(r['blocked_network_requests'])}; problems {len(r['problems'])}")
        for pr in r["problems"]:
            print("  ", pr)
        fail |= bool(r["problems"]) or bool(r["blocked_network_requests"])
    print("screenshots: outputs/dashboard_{390,1400}{,_filtered}.png")
    print("FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
