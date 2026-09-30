# 2026 replay: Area results → MOC entries

Run 2026-09-29: `python -m ncs_track replay --season 2026`. Inputs: 2026 Athletic.net
results for all four Area meets, `rules/2026.yaml`, and the 2026 MOC programs
(`moc_entries`). Outputs with athlete names are in `outputs/replay_2026/` (git-ignored);
this page has aggregates only. The rules were not adjusted to fit; the mismatches are the
finding.

## Best reading

All 32 combinations of the five rule switches were scored, with scratch pairing off.
Scratch pairing removes mismatches by construction, so it can't compete as a reading; it
is applied afterwards as an overlay.

| Switch | Best value |
|---|---|
| Class A at-large eligible from | 4th (Patrick's reading), not 7th |
| Fill spots vs at-large | fill first |
| Fill rule | MOC guide: 3 from all four meets (not NBL flyer: 6 from three Areas) |
| Tie at last fill spot | all tied marks in |
| Wind-aided marks for at-large | allowed |

This is the rules file's default reading.

| | Reading | + scratch pairs |
|---|---|---|
| Matched (incl. 2 spelling variants) | 763 | 763 |
| Predicted, not in program | 55 | 31 |
| In program, not predicted | 39 | 15 |
| Probable scratch-replacement pairs | – | 24 (48 rows) |
| **Match rate** matched / (matched + mismatches) | **89.0%** | 89.0% (94.7% counting pairs as explained) |
| Precision / recall | 93.3% / 95.1% | |
| Not comparable (school spelling unresolved) | 2 | 2 |

## By Area (reading, no scratch pairing)

| Area | Matched | Predicted, not entered | Entered, not predicted | Match rate |
|---|---|---|---|---|
| Bay Shore | 202 | 5 | 5 | 95.3% |
| Tri-Valley | 277 | 17 | 10 | 91.1% |
| Class A | 91 | 10 | 8 | 83.5% |
| Redwood Empire | 193 | 23 | 16 | 83.2% |

By event, 8 of 32 events match exactly. The lowest are girls 200 (60%), boys 1600 (70%),
girls 800 (75%) and boys 110H / girls 4x400 (78%). Full table:
`outputs/replay_2026/rates_by_event.csv`.

## Why entries differ

**Entered but not predicted (39).** Every one of them is in the Area final for the event,
so none is a name or school mismatch.
- 19 are the next marks just outside the 3 fill spots: 14 at fill rank 4, 2 at rank 5 and
  3 at rank 6.
- 20 are further down: below the standard, not auto, not fill.
- None meets the standard while being ineligible by place, so the Class A 4th-vs-7th
  question doesn't decide any 2026 entry.

**Predicted but not in the program (55).**
- **44 auto qualifiers.** 27 of them are entered in other MOC events. The likeliest
  explanations are event choice or an entry limit. 11 are absent from the MOC program
  entirely. 2 are one athlete whose school spelling ("California C") is unresolved; she
  *is* in the program.
- **7 fill and 4 at-large qualifiers.** 2 are entered in other events; the rest are
  absent.
- 4 of the 55 are relays.

**Scratch pairing** (a missing qualifier paired with the next finalist in line from the
same Area) explains 24 pairs. The fill-rank pattern above suggests some vacancies were
filled from the **fill line across all Areas** instead. That reading is not modelled yet.

## Which switches matter

Pairs of readings that differ in one switch only (16 pairs per switch):

| Switch | Changes predicted list | Mismatch change (min … max) |
|---|---|---|
| Fill source: MOC guide → NBL flyer | always | +30 … +103 |
| Fill before → after at-large | always | +22 … +61 |
| Fill ties included → excluded | always | −26 … +8 (worse at the best reading, +8) |
| Class A at-large from 4th → 7th | always | −3 … +5 (worse at the best reading, +3) |
| Wind-aided allowed → excluded | always | −5 … +6 (worse at the best reading, +6) |
| Scratch pairing off → on | never (comparison only) | −56 … −24 |

The fill rules decide the result. Class A eligibility and wind move it by a handful of
entries.
