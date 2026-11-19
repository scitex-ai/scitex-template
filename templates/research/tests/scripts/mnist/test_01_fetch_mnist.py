"""scripts/mnist/01_fetch_mnist.py: subset draw and pixel scaling."""

import numpy as np
import pytest
from conftest import load_script


@pytest.fixture(scope="module")
def fetch():
    return load_script("01_fetch_mnist")


@pytest.fixture
def labels():
    return np.arange(1_000) % 10


def test_training_subset_is_reproducible_for_a_seed(fetch, labels):
    # Arrange
    first = fetch.draw_training_subset(labels, 100, 7)
    # Act
    second = fetch.draw_training_subset(labels, 100, 7)
    # Assert
    assert np.array_equal(first, second)


def test_training_subset_changes_with_the_seed(fetch, labels):
    # Arrange
    first = fetch.draw_training_subset(labels, 100, 7)
    # Act
    other = fetch.draw_training_subset(labels, 100, 8)
    # Assert
    assert not np.array_equal(first, other)


def test_training_subset_has_no_repeated_index(fetch, labels):
    # Arrange
    n_train = 100
    # Act
    indices = fetch.draw_training_subset(labels, n_train, 7)
    # Assert
    assert len(np.unique(indices)) == n_train


def test_scale_pixels_flattens_each_image(fetch):
    # Arrange
    images = np.zeros((3, 28, 28), dtype=np.uint8)
    # Act
    flat = fetch.scale_pixels(images, 255)
    # Assert
    assert flat.shape == (3, 784)


def test_scale_pixels_maps_uint8_to_unit_interval(fetch):
    # Arrange
    images = np.array([[[0, 255], [128, 64]]], dtype=np.uint8)
    # Act
    flat = fetch.scale_pixels(images, 255)
    # Assert
    assert (flat.min(), flat.max()) == (0.0, 1.0)
