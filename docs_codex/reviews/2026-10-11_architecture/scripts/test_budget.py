#!/usr/bin/env python3
"""Formula, negative-input and useful boundary checks; no hardware simulation."""
import copy
import json
import unittest
from pathlib import Path

import budget


class BudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((Path(__file__).parent.parent / 'inputs/budget_inputs.json').read_text())
        cls.p = budget.unwrap(cls.raw['parameters'], cls.raw['sources'])

    def test_units_and_DDR_no_double_count(self):
        self.assertEqual(budget.ddr_bandwidth(16, 1333), 2_666_000_000)
        self.assertEqual(budget.ddr_bandwidth(64, 2133), 17_064_000_000)
        self.assertEqual(budget.axi_bandwidth(64, 250), 2_000_000_000)

    def test_image_packing_stride_and_sensitivity(self):
        self.assertEqual(budget.frame_bytes(12000, 12000, 16, 1), 288_000_000)
        self.assertEqual(budget.frame_bytes(12000, 12000, 12, 1), 216_000_000)
        self.assertEqual(budget.frame_bytes(12288, 12288, 16, 1), 301_989_888)
        self.assertEqual(budget.frame_bytes(3, 2, 12, 16), 32)

    def test_physical_sum_and_AXI_direction_are_separate(self):
        # A 1 GB frame, R+W=2, 10 GB/s DDR, 4 GB/s AXI each way -> 4 fps.
        self.assertEqual(budget.max_image_fps(1e9, 1, 1, 10e9, 4e9, 9e9, 0, 0), 4)
        self.assertEqual(budget.max_image_fps(1e9, 1, 1, 6e9, 4e9, 9e9, 0, 0), 3)
        self.assertEqual(budget.max_image_fps(1e9, 0, 1, 10e9, 4e9, 9e9, 0, 0), 4)
        self.assertEqual(budget.max_image_fps(1e9, 0, 1, 1e9, 4e9, 9e9, 1e9, 1e9), 0)
        self.assertIsNone(budget.max_image_fps(1e9, 0, 0, 1e9, 1e9, 1e9, 0, 0))

    def test_fifo_short_stall_and_deficit(self):
        x = budget.fifo_budget(8.64e9, 1.7329e9, 100, 2**20)
        self.assertAlmostEqual(x['needed_for_single_block_bytes'], 864_000)
        self.assertTrue(x['single_block_fits'])
        self.assertFalse(x['long_term_stable'])
        self.assertLess(x['empty_to_full_if_constant_deficit_s'], .0002)
        self.assertFalse(budget.fifo_budget(1e9, 1e9, 1, 1000)['long_term_stable'])
        self.assertTrue(budget.fifo_budget(2e9, 1.5e9, 1, 10000, 1e9)['long_term_stable'])

    def test_read_write_time_bound(self):
        # Independent R/W can overlap, while DDR sum cannot exceed its service.
        self.assertEqual(budget.transfer_time_lower_bound(4e9, 4e9, 10e9, 4e9, 4e9), 1)
        self.assertEqual(budget.transfer_time_lower_bound(4e9, 4e9, 4e9, 4e9, 4e9), 2)
        self.assertIsNone(budget.transfer_time_lower_bound(4e9, 0, 0, 4e9, 4e9))

    def test_kv_formula(self):
        self.assertEqual(budget.kv_bytes(24, 1, 4096, 8, 64, 16), 192 * 2**20)
        self.assertEqual(budget.kv_bytes(24, 2, 4096, 8, 64, 16), 384 * 2**20)

    def test_bad_values(self):
        for val in (-1, 0, float('nan'), float('inf'), True):
            with self.subTest(value=val), self.assertRaises(ValueError):
                budget.ddr_bandwidth(64, val)
        with self.assertRaises(ValueError):
            budget.axi_bandwidth(7, 250)
        with self.assertRaises(ValueError):
            budget.ddr_bandwidth(64, 1333, 1.01)
        with self.assertRaises(ValueError):
            budget.frame_bytes(1.5, 1, 8, 1)
        with self.assertRaises(ValueError):
            budget.kv_bytes(24, 0, 4096, 8, 64, 16)

    def test_provenance_required(self):
        with self.assertRaises(ValueError):
            budget.unwrap({'frequency': 250}, self.raw['sources'])
        with self.assertRaises(ValueError):
            budget.unwrap({'value': 250, 'source': 'missing', 'classification': 'assumption'}, self.raw['sources'])
        with self.assertRaises(ValueError):
            budget.unwrap({'value': 250, 'source': 'scenario'}, self.raw['sources'])

    def test_example_expected_findings(self):
        r = budget.calculate(copy.deepcopy(self.p))
        self.assertTrue(r['GB']['uniform_fits'])
        self.assertFalse(r['GB']['hotspot_fits'])
        self.assertFalse(r['GB']['double_buffer_can_hide_this_DMA_budget'])
        self.assertFalse(r['GB']['candidate_capacity_fits'][1]['fits'])
        self.assertTrue(r['GB']['candidate_capacity_fits'][2]['fits'])
        self.assertEqual(r['GEMM_tile_reloads']['unique_tensor_bytes'], 1_572_864)
        self.assertEqual(r['GEMM_tile_reloads']['no_cross_output_tile_reuse_bytes'], 5_242_880)
        self.assertEqual(r['GEMM_tile_reloads']['with_partial_sum_spills_bytes'], 11_534_336)
        x = next(x for x in r['image_limits'] if x['shape']=='12000x12000' and
                 x['format']=='raw16_packed' and x['hardware']=='x64_2133_ctrl256' and
                 x['pipeline']=='stream_ISP_then_write')
        self.assertEqual(x['max_fps_after_reservation'], 25)  # image AXI 256@250*.9
        self.assertFalse(x['meets_average_budget'])
        combined = next(x for x in r['combined_workloads'] if x['hardware']=='x64_2133_ctrl256' and
                        x['image_fps']==30 and x['pipeline']=='stream_ISP_then_write' and
                        x['inference']=='synthetic_CNN')
        self.assertTrue(combined['average_constraints']['DDR_total'])
        self.assertFalse(combined['average_constraints']['image_W'])
        json.dumps(r, allow_nan=False)

    def test_render_changed_fps_preserves_ROI_meaning(self):
        p = copy.deepcopy(self.p)
        p['image']['fps'] = 60
        r = budget.calculate(p)
        output = budget.render(r)
        self.assertIn('60 fps 的 ROI 面积占比上限', output)
        self.assertNotIn('30 fps 的 ROI 面积占比上限', output)
        # Same path ceiling (25 fps), doubled requested input (17.28 GB/s).
        self.assertIn('| x64_2133_ctrl256 | stream_ISP_then_write | 17.280 | 25.000 | 41.67% |', output)

    def test_render_changed_shape_and_custom_format(self):
        p = copy.deepcopy(self.p)
        p['image']['shapes'] = [{'id': 'custom_sensor', 'width': 2560, 'height': 1440}]
        p['image']['formats'] = [{'id': 'custom_packed10', 'sensor_bits': 10, 'storage_bits': 10}]
        p['image']['fps'] = 12.5
        r = budget.calculate(p)
        output = budget.render(r)
        self.assertIn('## 2560×1440、10-bit、12.5 fps 场景门限', output)
        self.assertNotIn('12000', output)
        self.assertIn('custom_sensor (2560×1440，12.5 fps)', output)
        self.assertIn('格式 `custom_packed10`', output)
        self.assertIn('| x64_2133_ctrl256 | stream_ISP_then_write | 0.058 |', output)
        self.assertEqual(r['image_formats'][0]['frame_bytes'], 4_608_000)
        self.assertAlmostEqual(r['image_formats'][0]['one_DDR_write_GB_s'], 0.0576)


if __name__ == '__main__':
    unittest.main(verbosity=2)
