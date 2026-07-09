#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-18 10:47:55 (ywatanabe)"
# File: /home/ywatanabe/proj/examples/scitex-research-template/scripts/mnist/05_plot_conf_mat.py


"""Plots confusion matrix from saved predictions and labels"""

# Imports
import scitex as stx
import numpy as np
from sklearn.metrics import confusion_matrix


# Functions and Classes
def plot_confusion_matrix(labels: np.ndarray, predictions: np.ndarray, CONFIG) -> None:
    cm = confusion_matrix(labels, predictions)
    fig, ax = stx.plt.subplots(figsize=(10, 8))
    ax.imshow(cm)
    ax.set_xyt("Predicted", "True", "Confusion Matrix")
    return fig


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rng_manager=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Plot confusion matrix"""
    predictions = stx.io.load("./data/mnist/predictions.npy")
    labels = stx.io.load("./data/mnist/labels.npy")
    fig = plot_confusion_matrix(labels, predictions, CONFIG)
    stx.io.save(
        fig,
        CONFIG.PATH.MNIST.FIGURES + "confusion_matrix.jpg",
        symlink_to="./data/mnist",
    )

    return 0


if __name__ == "__main__":
    main()

# EOF
