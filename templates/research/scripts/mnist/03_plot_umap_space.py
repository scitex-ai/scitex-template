#!/usr/bin/env python3


"""Creates UMAP visualization of MNIST dataset"""

# Imports
import figrecipe as plotting
import numpy as np
import scitex_io as io
import scitex_session as session
import umap


# Functions and Classes
def create_umap_embedding(data: np.ndarray, CONFIG) -> np.ndarray:
    reducer = umap.UMAP(random_state=CONFIG.MNIST.UMAP_RANDOM_STATE, n_jobs=-1)
    embedding = reducer.fit_transform(data)
    return embedding


def plot_umap(embedding: np.ndarray, labels: np.ndarray, CONFIG, plt) -> None:
    fig, ax = plotting.subplots(figsize=(12, 8))
    scatter = ax.scatter(
        embedding[:, 0], embedding[:, 1], c=labels, cmap="tab10", alpha=0.5
    )

    fig.colorbar(scatter, ax=ax)
    ax.set_xyt("UMAP 1", "UMAP 2", "UMAP Projection of MNIST Digits")

    return fig


@session.session
def main(
    CONFIG=session.INJECTED,
    plt=session.INJECTED,
    COLORS=session.INJECTED,
    rngg=session.INJECTED,
    logger=session.INJECTED,
):
    """Create UMAP visualization of MNIST"""
    train_data = io.load(CONFIG.PATH.MNIST.FLATTENED.TRAIN)
    train_labels = io.load(CONFIG.PATH.MNIST.LABELS.TRAIN)
    embedding = create_umap_embedding(train_data, CONFIG)
    fig = plot_umap(embedding, train_labels, CONFIG, plt)
    io.save(fig, CONFIG.PATH.MNIST.FIGURES + "umap.jpg", symlink_to="./data/mnist")

    return 0


if __name__ == "__main__":
    main()

# EOF
