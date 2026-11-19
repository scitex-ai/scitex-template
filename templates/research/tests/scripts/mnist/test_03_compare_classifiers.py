"""scripts/mnist/03_compare_classifiers.py: the paired 2x2 table."""

import numpy as np
import pytest
from conftest import load_script


@pytest.fixture(scope="module")
def compare():
    return load_script("03_compare_classifiers")


def test_paired_correctness_table_counts_each_cell(compare):
    # Arrange
    y = np.array([0, 1, 2, 3, 4])
    pred_a = np.array([0, 1, 9, 9, 4])  # right on 0, 1, 4
    pred_b = np.array([0, 9, 2, 9, 9])  # right on 0, 2
    # Act
    table = compare.paired_correctness_table(y, pred_a, pred_b)
    # Assert: [[both wrong, only b right], [only a right, both right]]
    assert table.tolist() == [[1, 1], [2, 1]]
