# Misfiled rows set out of scope

Decisions recorded in `data/reference/row_overrides.csv` and applied at ingest (V18). Each
override names the row it expects (meet, row, gender, event, place, mark). If the file
changes, ingest stops instead of touching the wrong row. No athlete names or IDs are
recorded here.

## 2022 Redwood Empire Area (Athletic.net meet 473068)

An adaptive race and flight were published inside the Varsity 100 m and long jump, in
both genders. Their winners appear as a second "place 1". Decided 2026-09-29: out of
scope, as misfiled adaptive results.

| Row | Gender | Event | Place | Mark | Note |
|---|---|---|---|---|---|
| 21 | Boys | 100 m | 1 | 17.14 | Second "place 1" (Varsity winner ran 10.76) |
| 22 | Boys | 100 m | X | 17.27 | Same race; already out of scope as exhibition |
| 312 | Boys | Long jump | 1 | 10-10.00 | Second "place 1" (Varsity winner 23-00.00) |
| 313 | Boys | Long jump | X | 9-09.00 | Same flight; already exhibition |
| 361 | Girls | 100 m | 1 | 17.85 | Second "place 1" (Varsity winner ran 12.26) |
| 362 | Girls | 100 m | X | 18.09 | Same race; already exhibition |
| 640 | Girls | Long jump | 1 | 10-06.00 | Second "place 1" (Varsity winner 17-10.00) |

With these set out of scope, the 2022 Redwood Empire file has no V06 place-order errors.
