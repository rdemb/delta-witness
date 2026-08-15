from __future__ import annotations

import unittest

from deltawitness.influence import compute_exact_influence_metrics


def exact(value: object) -> tuple[int, int]:
    if not isinstance(value, dict):
        raise AssertionError(f"Expected a rational document, received {value!r}")
    return int(value["numerator"]), int(value["denominator"])


def path_metrics(metrics: dict[str, object]) -> dict[str, dict[str, object]]:
    return {item["path"]: item for item in metrics["paths"]}  # type: ignore[index]


class ExactInfluenceMathTests(unittest.TestCase):
    def test_necessary_path_and_collateral_path(self) -> None:
        metrics = compute_exact_influence_metrics(
            ["src/core.py", "src/collateral.py"],
            {
                0: False,
                1: True,
                2: False,
                3: True,
            },
        )
        by_path = path_metrics(metrics)

        self.assertEqual(
            metrics["minimal_supported_coalitions"],
            [
                {
                    "coalition_id": "c1",
                    "mask": 1,
                    "paths": ["src/core.py"],
                    "size": 1,
                }
            ],
        )
        self.assertEqual(metrics["mandatory_paths"], ["src/core.py"])
        self.assertEqual(metrics["paths_in_no_minimal_coalition"], ["src/collateral.py"])
        self.assertEqual(exact(by_path["src/core.py"]["shapley"]), (1, 1))
        self.assertEqual(exact(by_path["src/core.py"]["normalized_banzhaf"]), (1, 1))
        self.assertEqual(exact(by_path["src/collateral.py"]["shapley"]), (0, 1))
        self.assertTrue(by_path["src/core.py"]["globally_necessary"])
        self.assertFalse(by_path["src/collateral.py"]["full_context_necessary"])

    def test_alternative_sufficient_paths_share_credit_and_are_redundant(self) -> None:
        metrics = compute_exact_influence_metrics(
            ["src/a.py", "src/b.py"],
            {
                0: False,
                1: True,
                2: True,
                3: True,
            },
        )
        by_path = path_metrics(metrics)

        self.assertEqual(len(metrics["minimal_supported_coalitions"]), 2)
        self.assertEqual(exact(by_path["src/a.py"]["shapley"]), (1, 2))
        self.assertEqual(exact(by_path["src/b.py"]["shapley"]), (1, 2))
        self.assertTrue(by_path["src/a.py"]["standalone_sufficient"])
        self.assertFalse(by_path["src/a.py"]["globally_necessary"])
        interaction = metrics["pair_interactions"][0]  # type: ignore[index]
        self.assertEqual(exact(interaction["normalized_banzhaf_interaction"]), (-1, 1))
        self.assertTrue(metrics["monotone_non_decreasing"])

    def test_jointly_necessary_paths_have_positive_interaction(self) -> None:
        metrics = compute_exact_influence_metrics(
            ["src/a.py", "src/b.py"],
            {
                0: False,
                1: False,
                2: False,
                3: True,
            },
        )
        by_path = path_metrics(metrics)

        self.assertEqual(exact(by_path["src/a.py"]["shapley"]), (1, 2))
        self.assertEqual(exact(by_path["src/b.py"]["shapley"]), (1, 2))
        self.assertTrue(by_path["src/a.py"]["globally_necessary"])
        self.assertTrue(by_path["src/b.py"]["globally_necessary"])
        interaction = metrics["pair_interactions"][0]  # type: ignore[index]
        self.assertEqual(exact(interaction["normalized_banzhaf_interaction"]), (1, 1))
        self.assertEqual(exact(metrics["shapley_efficiency_residual"]), (0, 1))

    def test_non_monotonic_truth_table_preserves_negative_influence(self) -> None:
        metrics = compute_exact_influence_metrics(
            ["src/a.py", "src/b.py"],
            {
                0: False,
                1: True,
                2: True,
                3: False,
            },
        )
        by_path = path_metrics(metrics)

        self.assertFalse(metrics["monotone_non_decreasing"])
        self.assertEqual(metrics["negative_edge_count"], 2)
        self.assertEqual(exact(by_path["src/a.py"]["shapley"]), (0, 1))
        self.assertEqual(exact(by_path["src/b.py"]["normalized_banzhaf"]), (0, 1))
        interaction = metrics["pair_interactions"][0]  # type: ignore[index]
        self.assertEqual(exact(interaction["normalized_banzhaf_interaction"]), (-2, 1))
        self.assertEqual(exact(metrics["endpoint_delta"]), (0, 1))
        self.assertEqual(exact(metrics["shapley_efficiency_residual"]), (0, 1))

    def test_incomplete_truth_table_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_exact_influence_metrics(
                ["src/a.py", "src/b.py"],
                {0: False, 1: True, 3: True},
            )


if __name__ == "__main__":
    unittest.main()
