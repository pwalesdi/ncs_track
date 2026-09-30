"""Allocation engine: who reaches the MOC under a given allocation config.

A generalisation of replay.evaluate. The replay answers "what do the current rules
predict?"; this engine answers the same question for any allocation described in a config
(configs/allocation/*.yaml):

  auto_spots      automatic places per Area (e.g. 6/6/6/3)
  fill            fill-spot count, pool of Areas, order vs at-large, ties at the cut
  at_large        standard on / off / adjusted (harder or easier by a % of the mark),
                  eligibility by place per Area, wind-aided marks allowed or not
  replacement     how vacancies are refilled when comparing with a real program
                  (off / same_area / fill_line); it never changes who is allocated

Standards always come from the season's rules file; the config says how to use them.
configs/allocation/current.yaml describes the existing system, and a test checks that the
engine with it reproduces the validated replay exactly for every season. The pass-down
scenarios (configs/allocation/a_5553, b_4443, c_3333) are run by ncs_track.scenarios, which
uses only auto_spots, fill and at_large from these configs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from . import replay
from .events import EVENTS
from .marks import parse_mark, sort_key
from .rules import mark_of

AREAS = replay.AREAS
EPS = replay.EPS


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class AllocationConfig:
    name: str
    auto_spots: dict                  # area -> places
    fill_count: int
    fill_pool: tuple                  # areas whose non-automatic marks compete for fill spots
    fill_order: str                   # before_at_large | after_at_large
    fill_ties: str                    # include | exclude
    at_large_mode: str                # on | off | adjusted
    at_large_adjust_pct: float        # adjusted: + makes every standard harder by this % of the mark
    at_large_outside_top: dict        # area -> eligible for at-large if Area place > this
    wind_aided_allowed: bool
    replacement: str                  # off | same_area | fill_line
    qualifying_rounds: tuple = ("final",)
    description: str = ""


def _areas_dict(d, what: str) -> dict:
    if not isinstance(d, dict) or set(d) != set(AREAS):
        raise ConfigError(f"{what} must give a value for exactly {list(AREAS)}")
    for a, v in d.items():
        if not isinstance(v, int) or v < 0:
            raise ConfigError(f"{what}.{a} must be a non-negative integer")
    return dict(d)


def load_config(path: Path) -> AllocationConfig:
    raw = yaml.safe_load(Path(path).read_text())
    try:
        fill, al = raw["fill"], raw["at_large"]
        cfg = AllocationConfig(
            name=raw["name"], description=raw.get("description", ""),
            auto_spots=_areas_dict(raw["auto_spots"], "auto_spots"),
            fill_count=int(fill["count"]), fill_pool=tuple(fill["pool"]),
            fill_order=fill["order"], fill_ties=fill["ties"],
            at_large_mode=al["mode"], at_large_adjust_pct=float(al.get("adjust_pct", 0)),
            at_large_outside_top=_areas_dict(al["eligible_outside_top"], "at_large.eligible_outside_top"),
            wind_aided_allowed=bool(al["wind_aided_allowed"]),
            replacement=raw["replacement"], qualifying_rounds=tuple(raw.get("qualifying_rounds", ["final"])),
        )
    except KeyError as e:
        raise ConfigError(f"{path}: missing key {e}") from None
    problems = []
    if cfg.fill_count < 0:
        problems.append("fill.count must be >= 0")
    if not set(cfg.fill_pool) <= set(AREAS):
        problems.append(f"fill.pool must be Areas from {list(AREAS)}")
    if cfg.fill_order not in ("before_at_large", "after_at_large"):
        problems.append("fill.order must be before_at_large or after_at_large")
    if cfg.fill_ties not in ("include", "exclude"):
        problems.append("fill.ties must be include or exclude")
    if cfg.at_large_mode not in ("on", "off", "adjusted"):
        problems.append("at_large.mode must be on, off or adjusted")
    if cfg.at_large_mode != "adjusted" and cfg.at_large_adjust_pct:
        problems.append("at_large.adjust_pct only applies when mode is adjusted")
    if cfg.replacement not in ("off", "same_area", "fill_line"):
        problems.append("replacement must be off, same_area or fill_line")
    if problems:
        raise ConfigError(f"{path}: " + "; ".join(problems))
    return cfg


def standard_value(cfg: AllocationConfig, rules: dict, gender: str, event: str) -> float | None:
    """The at-large standard the config applies (None = no at-large for this event)."""
    if cfg.at_large_mode == "off":
        return None
    entry = rules["area_to_moc"]["at_large"]["standards"].get(gender, {}).get(event)
    if entry is None:
        return None
    measure = EVENTS[event][0]
    v = parse_mark(mark_of(entry), measure).value
    if cfg.at_large_mode == "adjusted":
        f = cfg.at_large_adjust_pct / 100
        v = v * (1 - f) if measure == "time" else v * (1 + f)        # harder: faster time / longer mark
    return v


def allocate(results: pd.DataFrame, rules: dict, cfg: AllocationConfig) -> pd.DataFrame:
    """Every in-scope Area final performance, tagged auto / fill / at_large / None.

    Same columns as replay.evaluate, so replay.compare and the analysis tables accept it."""
    rounds = set(cfg.qualifying_rounds)
    df = results[(results["level"] == "area") & results["in_scope"].fillna(False)
                 & results["round"].isin(rounds)].copy()
    frames = []
    for gender, event in replay.main_events(rules):
        ev = df[(df["gender"] == gender) & (df["event_code"] == event)].copy()
        if ev.empty:
            continue
        measure = EVENTS[event][0]
        std = standard_value(cfg, rules, gender, event)
        ok = (ev["status"] == "OK") & ev["mark_value"].notna()
        place = ev["place"].astype("Float64")
        auto_n = ev["meet_area"].map(cfg.auto_spots).astype("Float64")
        ev["auto"] = (ok & place.notna() & (place <= auto_n)).fillna(False).astype(bool)
        if std is None:
            ev["meets_standard"] = False
        else:
            better = ev["mark_value"] <= std + EPS if measure == "time" else ev["mark_value"] >= std - EPS
            ev["meets_standard"] = (ok & better).fillna(False).astype(bool)
        eligible = (place > ev["meet_area"].map(cfg.at_large_outside_top).astype("Float64")).fillna(False)
        wind_ok = True if cfg.wind_aided_allowed else ~ev["wind_aided"].fillna(False).astype(bool)
        ev["at_large_eligible"] = (ok & ~ev["auto"] & eligible & wind_ok).astype(bool)
        ev["fill_candidate"] = (ok & ~ev["auto"] & ev["meet_area"].isin(cfg.fill_pool)).astype(bool)
        ev["standard_value"] = std

        at_large = ev["at_large_eligible"] & ev["meets_standard"]
        ties = cfg.fill_ties == "include"
        if cfg.fill_order == "before_at_large":
            fill_idx = replay._fill_pick(ev[ev["fill_candidate"]], cfg.fill_count, measure, ties)
            at_large &= ~ev.index.isin(fill_idx)
        else:
            fill_idx = replay._fill_pick(ev[ev["fill_candidate"] & ~at_large], cfg.fill_count, measure, ties)
        ranks = ev.loc[ev["fill_candidate"], "mark_value"].map(lambda v: sort_key(v, measure)).rank(method="min")
        ev["fill_rank"] = ranks.reindex(ev.index).astype("Int64")
        ev["qualified_by"] = None
        ev.loc[ev["auto"], "qualified_by"] = "auto"
        ev.loc[fill_idx, "qualified_by"] = "fill"
        ev.loc[at_large, "qualified_by"] = "at_large"
        frames.append(ev)
    if not frames:
        return pd.DataFrame(columns=replay.EVAL_COLUMNS)
    out = pd.concat(frames)
    out["interpretation"] = cfg.name
    return out[replay.EVAL_COLUMNS].reset_index(drop=True)


def overlay(cfg: AllocationConfig) -> replay.Interpretation:
    """The replay Interpretation carrying this config's comparison overlays."""
    return replay.Interpretation(name=cfg.name, replacement=cfg.replacement, entry_limit=0,
                                 fill_ties_include=cfg.fill_ties == "include")


def compare(allocated: pd.DataFrame, entries: pd.DataFrame, rules: dict, cfg: AllocationConfig,
            **kw) -> replay.Comparison:
    """Compare an allocation with a real MOC program (only meaningful for current.yaml)."""
    return replay.compare(allocated, entries, rules, interp=overlay(cfg), **kw)
