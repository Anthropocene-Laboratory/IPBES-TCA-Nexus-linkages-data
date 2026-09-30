# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""Check 18 frozen numerical expectations from the public CSV files.

    python verify.py

Reads only linkages.csv and nexus_response_options.csv. Passing these checks
validates the recorded expectations, not every claim in a manuscript revision.
"""
from __future__ import annotations

import collections
import csv
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MIN_CODERS = 2  # the agreement criterion the application itself applies

failures = []


def check(label: str, got, want) -> None:
    ok = got == want
    print("%-4s %-52s %s%s" % ("PASS" if ok else "FAIL", label, got, "" if ok else "  expected %s" % (want,)))
    if not ok:
        failures.append(label)


def read(name: str) -> list[dict]:
    with (HERE / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    links = read("linkages.csv")
    options = {row["id"]: row for row in read("nexus_response_options.csv")}

    # ---- the elicitation as a whole ---------------------------------------
    check("judgements recorded", len(links), 1692)
    check("coders with at least one judgement", len({l["coder"] for l in links}), 8)
    pairs = collections.defaultdict(list)
    for link in links:
        pairs[(link["tca_action_id"], link["nexus_option_id"])].append(link)
    check("distinct action-option pairs", len(pairs), 719)

    # ---- what the published figures are drawn from ------------------------
    kept = {key: rows for key, rows in pairs.items() if len({r["coder"] for r in rows}) >= MIN_CODERS}
    kept_links = [row for rows in kept.values() for row in rows]
    check("pairs above the agreement threshold", len(kept), 413)
    check("judgements they carry", len(kept_links), 1386)
    check("actions represented", len({k[0] for k in kept}), 22)
    check("response options represented", len({k[1] for k in kept}), 70)
    absent = sorted(set(options) - {k[1] for k in kept})
    check("the one option nobody retained", absent, ["W09"])

    strength = collections.Counter(row["strength"] for row in kept_links)
    check("primary judgements", strength["primary"], 665)
    check("secondary judgements", strength["secondary"], 721)
    split = sum(1 for rows in kept.values() if len({r["strength"] for r in rows}) > 1)
    check("pairs where coders divide on strength", split, 180)

    # ---- the primary-only variant (S2 Fig) --------------------------------
    primary_pairs = {
        key: rows
        for key, rows in pairs.items()
        if len({r["coder"] for r in rows if r["strength"] == "primary"}) >= MIN_CODERS
    }
    check("pairs with two primary judgements", len(primary_pairs), 162)
    # S2 Fig draws primary judgements only: the secondary ones recorded on those
    # same pairs are not shown, so they are not counted here either.
    check(
        "primary judgements they carry",
        sum(1 for rows in primary_pairs.values() for r in rows if r["strength"] == "primary"),
        572,
    )
    check("options they reach", len({k[1] for k in primary_pairs}), 62)

    # ---- concentration, the finding of section 4.3 ------------------------
    by_category = collections.Counter(options[k[1]]["category"] for k, rows in kept.items() for _ in rows)
    check("linkages reaching 'Ensure rights and equity'", by_category["Ensure rights and equity"], 287)
    check("linkages reaching 'Conserve ecosystems'", by_category["Conserve ecosystems"], 49)

    per_action = collections.defaultdict(collections.Counter)
    for key, rows in kept.items():
        per_action[key[0]][options[key[1]]["category"]] += len(rows)
    reach = sorted(len(counter) for counter in per_action.values())
    check("categories an action draws on, fewest and most", [reach[0], reach[-1]], [2, 9])
    shares = sorted(max(c.values()) / sum(c.values()) for c in per_action.values())
    check(
        "share carried by an action's largest category",
        [round(shares[0] * 100), round(shares[-1] * 100)],
        [21, 93],
    )

    print()
    if failures:
        print("%d of the article's numbers do not come out of this dataset." % len(failures))
        return 1
    print("All 18 recorded numerical expectations are reproduced by this dataset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
