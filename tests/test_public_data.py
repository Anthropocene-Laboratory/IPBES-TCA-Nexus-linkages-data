# SPDX-License-Identifier: MIT
import importlib.util
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from public_data import load_pairs


class PublicAnalysisTests(unittest.TestCase):
    def test_csv_pair_aggregation_matches_frozen_figure_populations(self):
        with patch.object(sys, 'argv', ['test']):
            pairs = load_pairs()
        kept = [p for p in pairs if p['coders'] >= 2]
        self.assertEqual(len(pairs), 719)
        self.assertEqual(len(kept), 413)
        self.assertEqual(sum(p['coders'] for p in kept), 1386)
        self.assertEqual(sum(p['primary'] for p in kept), 665)
        self.assertEqual(sum(p['secondary'] for p in kept), 721)
        self.assertEqual(len([p for p in pairs if p['primary'] >= 2]), 162)

    def test_entropy_extremes(self):
        spec = importlib.util.spec_from_file_location('versatility', ROOT / 'scripts/12_versatility.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertAlmostEqual(module.norm_entropy([10, 0, 0]), 0)
        self.assertAlmostEqual(module.norm_entropy([10, 10, 10]), 1)


if __name__ == '__main__':
    unittest.main()
