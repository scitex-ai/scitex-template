#!/usr/bin/env python3
# File: scripts/mnist/03_compare_classifiers.py

"""Compare the two classifiers on the same test images (scitex-stats).

McNemar's test uses the paired correctness of both classifiers on every
test image: only the images exactly one classifier got wrong carry
information. The full result (statistic, p-value, odds ratio, counts)
is saved as JSON so manuscript claims can point into it.
"""

import numpy as np
import scitex_io as sio
import scitex_session as sess
import scitex_stats as sst


def paired_correctness_table(y_true, pred_a, pred_b):
    """2x2 table [[both wrong, only B right], [only A right, both right]]."""
    a_ok = pred_a == y_true
    b_ok = pred_b == y_true
    return np.array(
        [
            [int(np.sum(~a_ok & ~b_ok)), int(np.sum(~a_ok & b_ok))],
            [int(np.sum(a_ok & ~b_ok)), int(np.sum(a_ok & b_ok))],
        ]
    )


def to_jsonable(result):
    """scitex-stats result dict -> plain JSON types."""
    out = {}
    for key, value in result.items():
        if isinstance(value, (np.generic,)):
            value = value.item()
        out[key] = value
    return out


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """McNemar's test: logistic regression vs RBF-SVM on the test set."""
    y_test = sio.load(eval(CONFIG.PATH.MNIST.Y_TEST))
    pred_logreg = sio.load(eval(CONFIG.PATH.RESULTS.PRED_LOGREG))
    pred_svc = sio.load(eval(CONFIG.PATH.RESULTS.PRED_SVC))

    table = paired_correctness_table(y_test, pred_logreg, pred_svc)
    cfg = CONFIG.STATS.MCNEMAR
    result = sst.test_mcnemar(
        table,
        var_before="logistic_regression",
        var_after="svc",
        correction=cfg.CONTINUITY_CORRECTION,
        alpha=cfg.ALPHA,
        decimals=cfg.DECIMALS,
    )
    out = {
        **to_jsonable(result),
        "table": table.tolist(),
        "n_test": len(y_test),
        "only_logreg_correct": int(table[1, 0]),
        "only_svc_correct": int(table[0, 1]),
    }
    sio.save(out, eval(CONFIG.PATH.RESULTS.MCNEMAR), symlink_from_cwd=True)
    logger.success(
        f"McNemar chi2={out['statistic']} p={out['pvalue']} "
        f"(only SVC right: {out['only_svc_correct']}, "
        f"only LogReg right: {out['only_logreg_correct']})"
    )
    return 0


if __name__ == "__main__":
    main()

# EOF
