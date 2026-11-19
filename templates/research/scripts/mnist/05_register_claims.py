#!/usr/bin/env python3
# File: scripts/mnist/05_register_claims.py

"""Register the manuscript's result numbers as claims (scitex-writer -> clew).

For every entry of config/CLAIMS.yaml this script reads the value from the
file a recorded run wrote (through scitex-io, so the read is recorded too),
rounds it to the precision the text shows, and registers it with
scitex-writer, which stores it in the scitex-clew claim store together with:

  * the manuscript location: the \\vclaim{<ID>} call site in the paper,
  * the source file and a JSON-pointer locator, so `clew verify` re-reads
    the value and compares it with what the text states.

A value is never typed here: if a source file is missing, or a \\vclaim is
not in the manuscript, registration fails loudly.
"""

import scitex_io as sio
import scitex_session as sess
import scitex_writer as sw


def resolve_pointer(document, pointer):
    """Value at an RFC 6901 JSON pointer (no escapes needed for our keys)."""
    node = document
    for part in pointer.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def source_path(CONFIG, dotted):
    """'RESULTS.METRICS' -> CONFIG.PATH.RESULTS.METRICS."""
    node = CONFIG.PATH
    for part in dotted.split("."):
        node = node[part]
    return node


def stated_value(raw, digits):
    """The value exactly as the manuscript writes it."""
    return round(float(raw)) if digits == 0 else round(float(raw), digits)


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """Register every claim of config/CLAIMS.yaml in the clew store."""
    workspace = CONFIG.PATH.PAPER.WORKSPACE
    loaded = {}
    for item in CONFIG.CLAIMS.ITEMS:
        path = source_path(CONFIG, item.SOURCE)
        if path not in loaded:
            loaded[path] = sio.load(path)
        value = stated_value(resolve_pointer(loaded[path], item.POINTER), item.DIGITS)
        result = sw.claim.add(
            workspace,
            item.ID,
            "value",
            {"value": value},
            context=item.CONTEXT,
            output_file=path.removeprefix("./"),
            source_keys={"value": {"pointer": item.POINTER}},
        )
        if not result.get("success"):
            raise RuntimeError(f"claim {item.ID!r} was not registered: {result}")
        logger.success(f"claim {item.ID} = {value}  <- {path}#{item.POINTER}")

    rendered = sw.claim.render(workspace)
    if not rendered.get("success"):
        raise RuntimeError(f"rendering \\vclaim values failed: {rendered}")
    return 0


if __name__ == "__main__":
    main()

# EOF
