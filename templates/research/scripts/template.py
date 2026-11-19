#!/usr/bin/env python3
# File: scripts/<topic>/NN_<verb>_<object>.py

"""Top-level docstring (becomes --help)."""

import scitex_session as sess


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """Read inputs with scitex_io.load, write outputs with scitex_io.save."""
    return 0


if __name__ == "__main__":
    main()

# EOF
