#!/usr/bin/env python3
# File: scripts/mnist/04_plot_figure.py

"""Figure 1 of the showcase manuscript, built with figrecipe.

Three panels are rendered at their final size in millimetres with the
SCITEX style, each saved with its recipe (YAML) and plotted data (CSV),
then composed from the recipes into one figure. No panel is ever
rescaled after rendering.

  A  one test image per digit (the first of each class, in test order)
  B  confusion matrix of the RBF-SVM on the test set
  C  per-class recall of both classifiers
"""

from pathlib import Path

import figrecipe as fr
import numpy as np
import scitex_io as sio
import scitex_session as sess

DIGITS = list(range(10))


def first_example_per_digit(X_test, y_test):
    """The first test image of each class (documented, not hand-picked)."""
    idx = [int(np.flatnonzero(y_test == d)[0]) for d in DIGITS]
    side = int(round(np.sqrt(X_test.shape[1])))  # flattened square images
    return X_test[idx].reshape(len(DIGITS), side, side)


def montage(images, n_cols):
    """Tile (n, h, w) images into one (rows*h, n_cols*w) array."""
    n_rows = int(np.ceil(len(images) / n_cols))
    h, w = images.shape[1:]
    canvas = np.zeros((n_rows * h, n_cols * w), dtype=images.dtype)
    for i, img in enumerate(images):
        r, c = divmod(i, n_cols)
        canvas[r * h : (r + 1) * h, c * w : (c + 1) * w] = img
    return canvas


def plot_digits(images, cfg):
    fig, ax = fr.subplots(
        axes_width_mm=cfg.W_MM, axes_height_mm=cfg.H_MM, constrained_layout=False
    )
    # Raw digit images, not a heatmap: no colour scale to read off.
    ax.imshow(montage(images, cfg.N_COLS), cmap=cfg.CMAP)  # stx-allow: STX-FM018
    ax.set_xytc(None, None, "Test images (first per digit)", caption=cfg.CAPTION)
    return fig


def row_fractions(conf_mat):
    """Each row (true digit) divided by its total: where that digit went."""
    return conf_mat / conf_mat.sum(axis=1, keepdims=True)


def plot_conf_mat(conf_mat, cfg):
    fig, ax = fr.subplots(
        axes_width_mm=cfg.W_MM, axes_height_mm=cfg.H_MM, constrained_layout=False
    )
    # Fraction of each true digit's test images per predicted digit, on a
    # fixed 0-1 scale.
    image = ax.imshow(row_fractions(conf_mat), cmap=cfg.CMAP, vmin=0, vmax=1)
    fig.colorbar(image, ax=ax, label="Fraction of true digit")
    ax.set_xticks(DIGITS)
    ax.set_yticks(DIGITS)
    ax.set_xytc("Predicted digit", "True digit", "RBF-SVM confusion", caption=cfg.CAPTION)
    return fig


def plot_recall(recall, cfg):
    fig, ax = fr.subplots(
        axes_width_mm=cfg.W_MM, axes_height_mm=cfg.H_MM, constrained_layout=False
    )
    ax.plot(recall["digit"], recall["LOGREG"], "o", label="Logistic regression")
    ax.plot(recall["digit"], recall["SVC"], "s", label="RBF-SVM")
    ax.set_xticks(DIGITS)
    ax.set_ylim(cfg.Y_MIN, 1)
    ax.set_xytc("Digit", "Recall (test set)", "Per-class recall", caption=cfg.CAPTION)
    ax.legend()
    return fig


def recipe_of(png_path):
    """Recipe YAML that figrecipe wrote next to a saved panel image."""
    return str(Path(png_path).resolve().with_suffix(".yaml"))


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """Render panels A-C and compose Figure 1 from their recipes."""
    fr.load_style(CONFIG.FIGURE.STYLE)
    P = CONFIG.PATH

    X_test = sio.load(P.MNIST.X_TEST)
    y_test = sio.load(P.MNIST.Y_TEST)
    conf_mat = sio.load(P.RESULTS.CONF_MAT_SVC).to_numpy()  # header = digits
    recall = sio.load(P.RESULTS.PER_CLASS_RECALL)

    panels = {
        P.FIGURES.PANEL_DIGITS: plot_digits(
            first_example_per_digit(X_test, y_test), CONFIG.FIGURE.DIGITS
        ),
        P.FIGURES.PANEL_CONF_MAT: plot_conf_mat(conf_mat, CONFIG.FIGURE.CONF_MAT),
        P.FIGURES.PANEL_RECALL: plot_recall(recall, CONFIG.FIGURE.RECALL),
    }
    # Each panel carries its caption (set_xytc) in its recipe; the figure
    # caption the reader sees is in the manuscript (figures/caption_and_media).
    for path, fig in panels.items():
        sio.save(fig, path, symlink_from_cwd=True)  # stx-allow: STX-FM019

    order = [P.FIGURES.PANEL_DIGITS, P.FIGURES.PANEL_CONF_MAT, P.FIGURES.PANEL_RECALL]
    # Panels keep their rendered mm size; the canvas is sized to fit them.
    fig, _ = fr.compose(
        sources={(0, i): recipe_of(path) for i, path in enumerate(order)},
        layout=(1, len(order)),
        gap_mm=CONFIG.FIGURE.COMPOSE.GAP_MM,
        panel_labels=True,
    )
    sio.save(  # stx-allow: STX-FM019
        fig, P.FIGURES.FIG1, symlink_from_cwd=True, derived_from=order
    )
    logger.success(f"Figure 1 -> {P.FIGURES.FIG1}")
    return 0


if __name__ == "__main__":
    main()

# EOF
