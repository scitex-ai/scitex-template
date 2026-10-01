#!/usr/bin/env python3


"""Top-level docstring here"""

# Imports
import scitex_session as session

# # Parameters
# CONFIG = scitex_config.load_configs() # For imported files using `./config/*.yaml`


# Functions and Classes
@session.session
def main(
    # arg1,
    # kwarg1="value1",
    CONFIG=session.INJECTED,
    plt=session.INJECTED,
    COLORS=session.INJECTED,
    rngg=session.INJECTED,
    logger=session.INJECTED,
):
    """Help message for `$ python __file__ --help`"""
    return 0


if __name__ == "__main__":
    main()

# EOF
