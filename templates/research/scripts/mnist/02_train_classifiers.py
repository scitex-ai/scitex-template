#!/usr/bin/env python3
# File: scripts/mnist/02_train_classifiers.py

"""Train two classifiers on the MNIST subset and evaluate on the test set.

The classifiers come from the scitex-ml factory (scikit-learn under the
hood) with the hyper-parameters in config/MNIST.yaml. Metrics come from
scitex_ml.metrics. This is the compute-heavy step (`make hpc` can run it
on a Slurm cluster instead).

Outputs: per-classifier test predictions (.npy), metrics.json (accuracy,
balanced accuracy, MCC), the SVC confusion matrix and per-class recall.
"""

import numpy as np
import pandas as pd
import scitex_io as sio
import scitex_ml
import scitex_repro
import scitex_session as sess


def build_classifier(spec, seed):
    """scitex-ml factory classifier with the configured hyper-parameters."""
    factory = scitex_ml.Classifier(random_state=seed)
    clf = factory(spec.NAME)
    # config keys are upper-cased at load: map them back to the estimator's
    # own parameter names (e.g. MAX_ITER -> max_iter, C -> C)
    names = {name.upper(): name for name in clf.get_params()}
    clf.set_params(**{names[key.upper()]: value for key, value in spec.PARAMS.items()})
    return clf


def evaluate(y_true, y_pred):
    """Test-set metrics of one classifier."""
    labels = sorted(np.unique(y_true).tolist())
    return {
        "accuracy": float(np.mean(y_true == y_pred)),
        "balanced_accuracy": float(
            scitex_ml.metrics.calc_bacc(y_true, y_pred, labels=labels)["value"]
        ),
        "mcc": float(
            scitex_ml.metrics.calc_mcc(y_true, y_pred, labels=labels)["value"]
        ),
        "n_test": len(y_true),
        "n_errors": int(np.sum(y_true != y_pred)),
    }


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """Train logistic regression and an RBF-SVM; evaluate both."""
    X_train = sio.load(eval(CONFIG.PATH.MNIST.X_TRAIN))
    y_train = sio.load(eval(CONFIG.PATH.MNIST.Y_TRAIN))
    X_test = sio.load(eval(CONFIG.PATH.MNIST.X_TEST))
    y_test = sio.load(eval(CONFIG.PATH.MNIST.Y_TEST))

    rsm = scitex_repro.RandomStateManager(seed=CONFIG.MNIST.CLASSIFIER_SEED)
    pred_paths = {
        "LOGREG": eval(CONFIG.PATH.RESULTS.PRED_LOGREG),
        "SVC": eval(CONFIG.PATH.RESULTS.PRED_SVC),
    }
    metrics = {"n_train": len(y_train)}
    predictions = {}
    for key, spec in CONFIG.MNIST.CLASSIFIERS.items():
        clf = build_classifier(spec, rsm.get_sklearn_random_state(key))
        logger.info(f"Training {spec.NAME} on {X_train.shape} ...")
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test).astype(np.int64)
        predictions[key] = y_pred
        metrics[key] = {"classifier": spec.NAME, **evaluate(y_test, y_pred)}
        sio.save(y_pred, pred_paths[key], symlink_from_cwd=True)
        logger.success(f"{spec.NAME}: accuracy={metrics[key]['accuracy']:.4f}")

    sio.save(metrics, eval(CONFIG.PATH.RESULTS.METRICS), symlink_from_cwd=True)

    labels = sorted(np.unique(y_test).tolist())
    conf_mat = scitex_ml.metrics.calc_conf_mat(
        y_test, predictions["SVC"], labels=labels
    )
    sio.save(
        pd.DataFrame(np.asarray(conf_mat["value"]), index=labels, columns=labels),
        eval(CONFIG.PATH.RESULTS.CONF_MAT_SVC),
        symlink_from_cwd=True,
    )

    recall = pd.DataFrame(
        {
            "digit": labels,
            **{
                key: [
                    float(np.mean(predictions[key][y_test == d] == d)) for d in labels
                ]
                for key in predictions
            },
        }
    )
    sio.save(
        recall, eval(CONFIG.PATH.RESULTS.PER_CLASS_RECALL), symlink_from_cwd=True, index=False
    )
    return 0


if __name__ == "__main__":
    main()

# EOF
