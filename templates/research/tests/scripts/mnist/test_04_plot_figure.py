"""scripts/mnist/04_plot_figure.py: example selection and tiling."""

import numpy as np
import pytest
from conftest import load_script


@pytest.fixture(scope="module")
def figure():
    return load_script("04_plot_figure")


def test_first_example_per_digit_takes_the_first_image_of_a_class(figure):
    # Arrange: digit 0 appears at index 1 and again at index 10
    side = 28  # MNIST image side
    y = np.array([3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 0])
    X = np.arange(len(y), dtype=np.float32)[:, None] * np.ones((1, side * side))
    # Act
    images = figure.first_example_per_digit(X, y)
    # Assert
    assert images[0, 0, 0] == 1.0


def test_montage_places_images_row_major(figure):
    # Arrange
    images = np.stack([np.full((2, 2), i) for i in range(4)])
    # Act
    canvas = figure.montage(images, 2)
    # Assert
    assert canvas[::2, ::2].tolist() == [[0, 1], [2, 3]]
