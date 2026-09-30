# Replay by season, 2022–2026

Run 2026-09-29. Each season uses its own rules file (`rules/{season}.yaml`: that season's
printed standards; allocations assumed from 2026; 2023 standards assumed from 2026) and
the best 2026 rule reading, held fixed:
- Class A at-large from 4th
- fill before at-large
- MOC-guide fill (3 from all four meets)
- fill ties included
- wind-aided marks allowed

Nothing was re-tuned per season. Command:

```
python -m ncs_track replay --season 2022 2023 2024 2025 --reading '{"class_a_at_large_outside_top":3,"fill_before_at_large":true,"fill_source":"moc_guide","fill_ties_include":true,"wind_aided_at_large":true}'
```

- **RAW** match rate = matched / (matched + every difference).
- **RULES** match rate = matched / (matched + differences not explained by athlete choice
  or replacement). The replacement overlay here is same-Area, which is best in every
  season.

| Season | Matched | RAW mismatches | RAW | RULES mismatches | RULES | RULES with fill-line replacement | Not comparable* |
|---|---|---|---|---|---|---|---|
| 2022 | 717 | 106 | 87.1% | 9 | 98.8% | 97.3% | 15 |
| 2023 | 745 | 101 | 88.1% | 10 | 98.7% | 97.8% | 5 |
| 2024 | 756 | 99 | 88.4% | 16 | 97.9% | 97.4% | 0 |
| 2025 | 749 | 97 | 88.5% | 7 | 99.1% | 96.9% | 0 |
| 2026 | 765 | 92 | 89.3% | 15 | 98.1% | 97.2% | 0 |

\* Program entries whose school spelling has no area that season, so they can't be
compared:
- 2022: "West County" (12 entries), an unconfirmed rename kept in review, and "St. Joseph
  N" (3).
- 2023: two Kennedy spellings (3) and "Tech HS" (2), a school with no Area participation
  on Athletic.net.

**No season is much worse than 2026.** RAW rates span 87.1–89.3% and RULES rates 97.9–99.1%.
The entry limit (assumed 4) explains nothing in any season.
