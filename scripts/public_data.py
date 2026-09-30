# SPDX-License-Identifier: MIT
"""Load only the deposited public CSVs; no database, workbook or identity map."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, default=ROOT / 'outputs')
    return parser.parse_args()


def read(name):
    with (arguments().data / name).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def action_index():
    result = {}
    for row in read('tca_actions.csv'):
        head, label = row['action'].split(':', 1)
        result[row['id']] = dict(row, code=head.replace('Action', '').strip(),
                                label=label.strip(),
                                strategy_num=int(row['strategy'].split(':')[0].replace('Strategy', '').strip()))
    return result


def option_index():
    return {row['id']: row for row in read('nexus_response_options.csv')}


def load_pairs():
    actions, options = action_index(), option_index()
    pairs = defaultdict(lambda: {'coders': 0, 'primary': 0, 'secondary': 0})
    seen = set()
    for row in read('linkages.csv'):
        key = (row['tca_action_id'], row['nexus_option_id'])
        judgement = (row['coder'], *key)
        if key[0] not in actions or key[1] not in options:
            raise ValueError(f'Unknown reference: {key}')
        if row['strength'] not in {'primary', 'secondary'}:
            raise ValueError('Unknown judgement strength')
        if judgement in seen:
            raise ValueError(f'Duplicate coder judgement for pair: {key}')
        seen.add(judgement)
        pairs[key]['coders'] += 1
        pairs[key][row['strength']] += 1
    # The original Table C was ordered by coder count, then action/option ID.
    ordered = sorted(pairs.items(), key=lambda item: (-item[1]['coders'], '|'.join(item[0])))
    return [dict(values, action=key[0], option=key[1], category=options[key[1]]['category'])
            for key, values in ordered]


def write(name, text):
    args = arguments()
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / name
    target.write_text(text, encoding='utf-8')
    manifest = {
        'inputs_sha256': {file: hashlib.sha256((args.data / file).read_bytes()).hexdigest()
                         for file in ('linkages.csv', 'tca_actions.csv', 'nexus_response_options.csv')},
        'output': name,
        'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    }
    target.with_suffix('.provenance.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'-> {target}')
    return target
