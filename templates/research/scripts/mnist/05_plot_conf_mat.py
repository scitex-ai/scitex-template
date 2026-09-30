#!/usr/bin/env python3


"""Plots confusion matrix from saved predictions and labels"""

# Imports
import figrecipe as plotting
import numpy as np
import scitex_io as io
import scitex_session as session
from sklearn.metrics import confusion_matrix


# Functions and Classes
def plot_confusion_matrix(labels: np.ndarray, predictions: np.ndarray, CONFIG) -> None:
    cm = confusion_matrix(labels, predictions)
    fig, ax = plotting.subplots(figsize=(10, 8))
    ax.imshow(cm)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion Matrix")
    return fig


@session.session
def main(
    CONFIG=session.INJECTED,
    plt=session.INJECTED,
    COLORS=session.INJECTED,
    rngg=session.INJECTED,
    logger=session.INJECTED,
):
    """Plot confusion matrix"""
    predictions = io.load("./data/mnist/predictions.npy")
    labels = io.load("./data/mnist/labels.npy")
    fig = plot_confusion_matrix(labels, predictions, CONFIG)
    io.save(
        fig,
        CONFIG.PATH.MNIST.FIGURES + "confusion_matrix.jpg",
        symlink_to="./data/mnist",
    )

    return 0


if __name__ == "__main__":
    main()

# EOF
