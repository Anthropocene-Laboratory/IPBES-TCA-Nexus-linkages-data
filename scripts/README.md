# Public analysis code

These are the public counterparts of the project's two publication-analysis
scripts, ported from the supplementary workbook to the deposited CSV files.
They require Python 3.10+ and only the standard library. No private loader,
identity map, database export or manuscript history is included.

- `11_figure_patterns.py`: per-action category concentration, category totals,
  response-option reach across actions and strategies, and multi-action coverage.
- `12_versatility.py`: reach, normalised Shannon breadth, and sensitivity to
  dropping the two-coder threshold.
- `public_data.py`: strict pair aggregation and public reference lookup.

A pair is retained when at least two distinct coders identify it, independently
of strength. Link weights count judgements. Duplicate coder/pair rows fail rather
than inflate agreement. The primary-only figure separately requires two primary
judgements, as checked by `verify.py` and the tests.

Historical calculation conventions are preserved: Table C order is descending
coder count followed by action/option ID. Equal reach values keep this order in
rank tables. The historical ordinal rank-comparison score is retained and named
as such; it is not a tie-aware Spearman correlation. Interpret rank shifts with
that limitation. No significance or causal interpretation is claimed.

Draft-review commentary and fixed narrative conclusions were removed. The
numerical tables, weighting, entropy definition and thresholds are preserved.
The input/output checksums written next to reports identify each run.

```bash
python scripts/11_figure_patterns.py --out outputs
python scripts/12_versatility.py --out outputs
```

Licence: MIT (../LICENSE-CODE).
