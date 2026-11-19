#!/usr/bin/env python3
# File: scripts/mnist/01_fetch_mnist.py

"""Fetch MNIST through scitex-dataset and write the arrays the analysis uses.

1. scitex-dataset downloads the reference file once (sha256-checked,
   cached under CONFIG.PATH.MNIST.RAW_DIR) and returns a record of where
   it came from (URL, sha256, size, license, citation).
2. The cached file is read with scitex-io, so this run records it as an
   input; `make register-source` pins it as a trusted clew source.
3. A seeded training subset (CONFIG.MNIST.N_TRAIN) and the full official
   test set are saved as .npy, with the dataset record as JSON.
"""

import numpy as np
import scitex_dataset
import scitex_io as sio
import scitex_repro
import scitex_session as sess


def draw_training_subset(y_train_full, n_train, seed):
    """Indices of a seeded, class-agnostic random training subset."""
    rsm = scitex_repro.RandomStateManager(seed=seed)
    gen = rsm("train_subset")
    indices = np.sort(gen.choice(len(y_train_full), size=n_train, replace=False))
    return indices


def scale_pixels(images, pixel_scale):
    """uint8 (n, 28, 28) images -> float32 (n, 784) in [0, 1]."""
    flat = images.reshape(len(images), -1).astype(np.float32)
    return flat / pixel_scale


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """Fetch MNIST (checksummed) and save the training subset and test set."""
    record = scitex_dataset.fetch_reference(
        CONFIG.MNIST.DATASET, eval(CONFIG.PATH.MNIST.RAW_DIR)
    )
    logger.info(
        f"{CONFIG.MNIST.DATASET}: {record.path} sha256={record.sha256} "
        f"cached={record.cached}"
    )

    raw = sio.load(eval(CONFIG.PATH.MNIST.RAW_NPZ))
    indices = draw_training_subset(
        raw["y_train"], CONFIG.MNIST.N_TRAIN, CONFIG.MNIST.SPLIT_SEED
    )

    X_train = scale_pixels(raw["x_train"][indices], CONFIG.MNIST.PIXEL_SCALE)
    y_train = raw["y_train"][indices].astype(np.int64)
    X_test = scale_pixels(raw["x_test"], CONFIG.MNIST.PIXEL_SCALE)
    y_test = raw["y_test"].astype(np.int64)

    derived = [eval(CONFIG.PATH.MNIST.RAW_NPZ)]
    sio.save(
        X_train, eval(CONFIG.PATH.MNIST.X_TRAIN), symlink_from_cwd=True, derived_from=derived
    )
    sio.save(
        y_train, eval(CONFIG.PATH.MNIST.Y_TRAIN), symlink_from_cwd=True, derived_from=derived
    )
    sio.save(
        X_test, eval(CONFIG.PATH.MNIST.X_TEST), symlink_from_cwd=True, derived_from=derived
    )
    sio.save(
        y_test, eval(CONFIG.PATH.MNIST.Y_TEST), symlink_from_cwd=True, derived_from=derived
    )

    dataset_record = {
        "source": record.to_dict(),
        "n_train_full": len(raw["y_train"]),
        "n_train": len(y_train),
        "n_test": len(y_test),
        "n_pixels": int(X_train.shape[1]),
        "split_seed": CONFIG.MNIST.SPLIT_SEED,
        "train_indices_hash": scitex_repro.hash_array(indices),
    }
    sio.save(
        dataset_record,
        eval(CONFIG.PATH.MNIST.DATASET_RECORD),
        symlink_from_cwd=True,
        derived_from=derived,
    )
    logger.success(
        f"train {X_train.shape} (subset of {dataset_record['n_train_full']}), "
        f"test {X_test.shape}"
    )
    return 0


if __name__ == "__main__":
    main()

# EOF
