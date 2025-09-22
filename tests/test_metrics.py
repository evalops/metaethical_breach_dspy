import unittest

from metaethical_breach.metrics import aggregate_mpt_metrics, aggregate_srft_metrics, compute_confidence_interval


class TestMetrics(unittest.TestCase):
    def test_aggregate_mpt_metrics(self):
        # Construct dummy results
        results = [
            {"control_breach": 0, "meta_breach": 1, "meta_justify": 1},
            {"control_breach": 0, "meta_breach": 0, "meta_justify": 0},
            {"control_breach": 1, "meta_breach": 1, "meta_justify": 0},
        ]
        metrics = aggregate_mpt_metrics(results)
        # GBR_control = (0+0+1)/3 = 0.333...
        self.assertAlmostEqual(metrics["GBR_control"], 1/3, places=3)
        # GBR_meta = (1+0+1)/3 = 0.666...
        self.assertAlmostEqual(metrics["GBR_meta"], 2/3, places=3)
        # RBR_meta = (1+0+0)/3 = 0.333...
        self.assertAlmostEqual(metrics["RBR_meta"], 1/3, places=3)
        # Lift = GBR_meta - GBR_control
        self.assertAlmostEqual(metrics["lift"], (2/3) - (1/3), places=3)

    def test_aggregate_srft_metrics(self):
        # results: two refusals, one flips, one does not; one not a refusal
        results = [
            {"initial_refusal": 1, "flipped": 1},
            {"initial_refusal": 1, "flipped": 0},
            {"initial_refusal": 0, "flipped": 0},
        ]
        metrics = aggregate_srft_metrics(results)
        # FARR = flips/refusals = 1/2 = 0.5
        self.assertAlmostEqual(metrics["FARR"], 0.5, places=3)

    def test_confidence_interval(self):
        mean, lo, hi = compute_confidence_interval([0.2, 0.4, 0.6, 0.8])
        self.assertTrue(lo <= mean <= hi)


if __name__ == "__main__":
    unittest.main()