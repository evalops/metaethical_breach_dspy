import unittest

from metaethical_breach.data import get_dev_labeled, get_train_unlabeled


class TestData(unittest.TestCase):
    def test_dev_dataset_counts(self):
        dev = get_dev_labeled()
        self.assertEqual(len(dev), 15, "Expected 15 examples in the development set")
        # Count verdicts
        yes = sum(1 for ex in dev if ex.get("verdict") == "yes")
        no = sum(1 for ex in dev if ex.get("verdict") == "no")
        self.assertEqual(yes, 5, "Expected 5 benign examples labeled 'yes'")
        self.assertEqual(no, 10, "Expected 10 harmful examples labeled 'no'")

    def test_train_dataset_length(self):
        reps = 4
        train = get_train_unlabeled(repetitions=reps)
        # Should be 10 harmful requests repeated reps times
        self.assertEqual(len(train), 10 * reps)


if __name__ == "__main__":
    unittest.main()