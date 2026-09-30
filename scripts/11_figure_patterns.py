# SPDX-License-Identifier: MIT
"""Public CSV reproduction of the mapping-pattern analysis. Python 3.10+, standard library only."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from public_data import action_index, option_index, load_pairs, write

MIN_CODERS = 2

L = []


def say(s=""):
    L.append(str(s))


def main() -> None:
    actions = action_index()
    options = option_index()
    all_pairs = load_pairs()
    kept = [p for p in all_pairs if p["coders"] >= MIN_CODERS]
    links = sum(p["coders"] for p in kept)

    say("PATTERNS IN THE ACTION x RESPONSE-OPTION MAPPING")
    say("=" * 78)
    say("Source        : public linkages.csv and reference CSV files")
    say(f"Threshold     : pairs coded by >= {MIN_CODERS} experts")
    say(f"Pairs         : {len(kept)} of {len(all_pairs)}")
    say(f"Links         : {links} of {sum(p['coders'] for p in all_pairs)}")
    say()

    # ------------------------------------------------------------------ 1
    say("1. CONCENTRATION OF LINKAGES BY ACTION")
    say("-" * 78)
    say("Even spread would put 10% of an action's links in each of the 10 categories.")
    say()
    grid = defaultdict(lambda: defaultdict(int))
    for p in kept:
        grid[p["action"]][p["category"]] += p["coders"]

    say(f"{'action':<7} {'links':>6} {'cats':>5} {'top share':>10}  top category")
    rows = []
    for aid, row in grid.items():
        total = sum(row.values())
        top, topv = max(row.items(), key=lambda kv: kv[1])
        rows.append((actions[aid]["code"], total, len(row), topv / total, top))
    for code, total, ncat, share, top in sorted(rows):
        say(f"{code:<7} {total:>6} {ncat:>5} {share:>9.0%}  {top}")
    say()
    shares = [r[3] for r in rows]
    ncats = [r[2] for r in rows]
    say(f"Categories reached per action : {min(ncats)}-{max(ncats)} of 10 (even spread would be 10)")
    say(f"Share in the largest category : {min(shares):.0%}-{max(shares):.0%} (even spread would be 10%)")
    say(f"Actions above 50% in one category: {sum(1 for s in shares if s > 0.5)} of {len(shares)}")
    say()

    # ------------------------------------------------------------------ 2
    say("2. THE CATEGORIES ARE NOT EQUALLY DRAWN ON")
    say("-" * 78)
    cat_links = defaultdict(int)
    cat_top_for = defaultdict(int)
    for code, total, ncat, share, top in rows:
        cat_top_for[top] += 1
    for p in kept:
        cat_links[p["category"]] += p["coders"]
    say(f"{'nexus category':<36} {'links':>6} {'share':>7} {'top for':>8}")
    for cat, v in sorted(cat_links.items(), key=lambda kv: -kv[1]):
        say(f"{cat:<36} {v:>6} {v / links:>6.1%} {cat_top_for[cat]:>7} actions")
    say()

    # ------------------------------------------------------------------ 3
    say("3. WHICH RESPONSE OPTIONS CUT ACROSS THE MOST ACTIONS")
    say("-" * 78)
    say("Cross-cutting = reached from many different actions, and from >1 strategy.")
    say()
    opt_actions = defaultdict(set)
    opt_links = defaultdict(int)
    for p in kept:
        opt_actions[p["option"]].add(p["action"])
        opt_links[p["option"]] += p["coders"]
    say(f"{'option':<9} {'actions':>8} {'strat':>6} {'links':>6}  title")
    ranked = sorted(opt_actions.items(), key=lambda kv: (-len(kv[1]), -opt_links[kv[0]]))
    for oid, acts in ranked[:20]:
        strategies = {actions[a]["strategy_num"] for a in acts}
        say(f"{oid:<9} {len(acts):>8} {len(strategies):>6} {opt_links[oid]:>6}  {options[oid]['title'][:44]}")
    say()
    say(f"Response options reached from all 5 strategies: "
        f"{sum(1 for oid, a in opt_actions.items() if len({actions[x]['strategy_num'] for x in a}) == 5)} "
        f"of {len(opt_actions)}")
    say(f"Median actions per response option: "
        f"{sorted(len(a) for a in opt_actions.values())[len(opt_actions) // 2]}")
    say()

    # ------------------------------------------------------------------ 5
    say("4. RESPONSE OPTIONS LINKED TO MULTIPLE ACTIONS")
    say("-" * 78)
    counts = sorted(len(a) for a in opt_actions.values())
    for k in (1, 2, 3, 5, 10):
        say(f"reached from >= {k:>2} actions: {sum(1 for c in counts if c >= k):>3} of {len(counts)} options")
    say()
    multi_strategy = sum(
        1 for a in opt_actions.values() if len({actions[x]["strategy_num"] for x in a}) > 1
    )
    say(f"Reached from more than one TCA strategy: {multi_strategy} of {len(opt_actions)} options "
        f"({multi_strategy / len(opt_actions):.0%})")

    write("11_figure_patterns.txt", "\n".join(L) + "\n")


if __name__ == "__main__":
    main()
