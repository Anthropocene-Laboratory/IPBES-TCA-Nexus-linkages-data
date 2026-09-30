# SPDX-License-Identifier: MIT
"""Public CSV reproduction of the reach and breadth analysis. Python 3.10+, standard library only."""
from __future__ import annotations

import math
from collections import defaultdict

from public_data import action_index, option_index, load_pairs, write

SHORT = {
    "1.1": "Territories of Life", "1.2": "Biodiversity Rights", "1.3": "Diverse Values",
    "1.4": "Regenerative Land Use", "1.5": "Integrated Planning",
    "2.1": "Exploitation Regulation", "2.2": "Transformative Technology",
    "2.3": "Sustainability Finance", "2.4": "Civil Society",
    "3.1": "Economic Innovation", "3.2": "Just Transitions", "3.3": "Financial Reform",
    "3.4": "New success Metrics", "4.1": "Integrated Governance", "4.2": "Inclusive Governance",
    "4.3": "Multilateral Governance", "4.4": "Adaptive Governance",
    "5.1": "Nature Connectedness", "5.2": "New Narratives", "5.3": "Social Norms",
    "5.4": "Transformative Learning", "5.5": "Knowledge Co-creation",
}

L = []


def say(s=""):
    L.append(str(s))


def norm_entropy(counts: list[int]) -> float:
    """Normalised Shannon entropy. 1 = spread evenly over all groups, 0 = one group."""
    total = sum(counts)
    if total == 0 or len(counts) <= 1:
        return 0.0
    h = -sum((c / total) * math.log(c / total) for c in counts if c)
    return abs(h / math.log(len(counts)))


def profile(pairs, actions, options):
    """Reach, breadth and links for every action and every response option."""
    a_opts, a_links, a_cat = defaultdict(set), defaultdict(int), defaultdict(lambda: defaultdict(int))
    o_acts, o_links, o_strat = defaultdict(set), defaultdict(int), defaultdict(lambda: defaultdict(int))
    for p in pairs:
        s = actions[p["action"]]["strategy_num"]
        a_opts[p["action"]].add(p["option"])
        a_links[p["action"]] += p["coders"]
        a_cat[p["action"]][p["category"]] += p["coders"]
        o_acts[p["option"]].add(p["action"])
        o_links[p["option"]] += p["coders"]
        o_strat[p["option"]][s] += p["coders"]

    cats = sorted({p["category"] for p in pairs})
    acts_out = []
    for aid, opts in a_opts.items():
        counts = [a_cat[aid].get(c, 0) for c in cats]
        acts_out.append({
            "id": aid, "code": actions[aid]["code"], "name": SHORT[actions[aid]["code"]],
            "reach": len(opts), "links": a_links[aid],
            "groups": sum(1 for c in counts if c), "breadth": norm_entropy(counts),
        })
    opts_out = []
    for oid, acts in o_acts.items():
        counts = [o_strat[oid].get(s, 0) for s in (1, 2, 3, 4, 5)]
        opts_out.append({
            "id": oid, "name": options[oid]["title"], "category": options[oid]["category"],
            "reach": len(acts), "links": o_links[oid],
            "groups": sum(1 for c in counts if c), "breadth": norm_entropy(counts),
        })
    return acts_out, opts_out


def table(rows, kind, group_label, total_possible):
    say(f"{'rank':>4} {'id':<9} {'name':<28} {'reach':>6} {group_label:>7} {'breadth':>8} {'links':>6}")
    for i, r in enumerate(sorted(rows, key=lambda x: (-x["reach"], -x["links"])), 1):
        say(f"{i:>4} {r.get('code', r['id']):<9} {r['name'][:28]:<28} "
            f"{r['reach']:>6} {r['groups']:>7} {r['breadth']:>8.2f} {r['links']:>6}")
    say(f"(reach = distinct {kind} linked, out of {total_possible} possible)")


def main() -> None:
    actions, options = action_index(), option_index()
    all_pairs = load_pairs()
    kept = [p for p in all_pairs if p["coders"] >= 2]
    acts, opts = profile(kept, actions, options)

    say("VERSATILITY OF TCA ACTIONS AND NXS RESPONSE OPTIONS")
    say("=" * 92)
    say("Reach   = number of distinct partners linked.")
    say("Groups  = number of partner groups touched (10 Nexus categories / 5 TCA strategies).")
    say("Breadth = normalised entropy of the link distribution over those groups.")
    say("          1.00 = spread evenly over every group, 0.00 = everything in one group.")
    say(f"Threshold: pairs coded by at least 2 experts. {len(kept)} pairs, {sum(p['coders'] for p in kept):,} links.")
    say()

    say("1. TCA ACTIONS, ranked by how many response options they reach")
    say("-" * 92)
    table(acts, "response options", "cats", 71)
    say()

    say("2. NXS RESPONSE OPTIONS, ranked by how many actions they reach")
    say("-" * 92)
    table(opts, "actions", "strats", 22)
    reached = {x["id"] for x in opts}
    missing = [oid for oid in options if oid not in reached]
    say(f"Response options reaching no action at this threshold: {missing or 'none'}")
    say()

    say("3. WHERE REACH AND BREADTH DISAGREE — the actual 'polyfacetic' question")
    say("-" * 92)
    say("An action can reach many options that all sit in one category. That is volume,")
    say("not versatility. Ranking each action on both and comparing the two ranks isolates")
    say("the cases where the two readings part company.")
    say()
    by_reach = {r["code"]: i for i, r in enumerate(sorted(acts, key=lambda x: -x["reach"]), 1)}
    by_breadth = {r["code"]: i for i, r in enumerate(sorted(acts, key=lambda x: -x["breadth"]), 1)}
    say(f"{'code':<6} {'name':<28} {'rank reach':>11} {'rank breadth':>13} {'shift':>6}")
    for r in sorted(acts, key=lambda x: by_breadth[x["code"]] - by_reach[x["code"]]):
        shift = by_breadth[r["code"]] - by_reach[r["code"]]
        say(f"{r['code']:<6} {r['name'][:28]:<28} {by_reach[r['code']]:>11} "
            f"{by_breadth[r['code']]:>13} {shift:>+6}")
    say()
    say("Negative shift = broader than its reach suggests (versatile on few partners).")
    say("Positive shift = narrower than its reach suggests (volume concentrated in few categories).")
    say()

    say("4. ROBUSTNESS: does the ranking survive dropping the agreement threshold?")
    say("-" * 92)
    acts_all, opts_all = profile(all_pairs, actions, options)
    for label, kept_rows, all_rows, key in (
        ("actions", acts, acts_all, "code"),
        ("response options", opts, opts_all, "id"),
    ):
        r_kept = {r[key]: i for i, r in enumerate(sorted(kept_rows, key=lambda x: -x["reach"]), 1)}
        r_all = {r[key]: i for i, r in enumerate(sorted(all_rows, key=lambda x: -x["reach"]), 1)}
        shared = [k for k in r_kept if k in r_all]
        moves = sorted(((abs(r_kept[k] - r_all[k]), k) for k in shared), reverse=True)
        n = len(shared)
        # Historical ordinal comparison, preserving the original calculation.
        # Ties keep table order; this is not tie-aware Spearman correlation.
        d2 = sum((r_kept[k] - r_all[k]) ** 2 for k in shared)
        rho = 1 - (6 * d2) / (n * (n * n - 1)) if n > 2 else float("nan")
        say(f"{label:<18} Historical ordinal rank score (ties keep table order): {rho:.3f}")
        # A whole-ranking correlation hides where the instability sits. Split the
        # ranking into its top, middle and bottom and report each, because a rank
        # that only holds at the top means only the top may be quoted.
        for band, members in (
            ("top 10", [k for k in shared if r_kept[k] <= 10]),
            ("middle", [k for k in shared if 10 < r_kept[k] <= n - 10]),
            ("bottom 10", [k for k in shared if r_kept[k] > n - 10]),
        ):
            if not members:
                continue
            moves = sorted(abs(r_kept[k] - r_all[k]) for k in members)
            worst = max(members, key=lambda k: abs(r_kept[k] - r_all[k]))
            say(f"{'':<18}   {band:<10} median move {moves[len(moves) // 2]:>4.1f}  "
                f"max {moves[-1]:>3}  (worst: {worst} moves {r_kept[worst]} -> {r_all[worst]})")
        say()

    say("Ranks use stable table order to break ties; rank shifts and the historical")
    say("ordinal score are sensitive to that convention. They are descriptive,")
    say("not a tie-aware Spearman test or evidence of a causal mechanism.")

    write("12_versatility.txt", "\n".join(L) + "\n")


if __name__ == "__main__":
    main()
