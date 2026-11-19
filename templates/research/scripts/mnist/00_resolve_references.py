#!/usr/bin/env python3
# File: scripts/mnist/00_resolve_references.py

"""Resolve and enrich the manuscript's references with scitex-scholar.

ONLINE and optional (`make refs`): the resolved bibliography is committed,
so the default `make all` runs offline. Re-run this only to refresh it.

Input : CONFIG.PATH.LITERATURE.SEED_BIB  (title + year + DOI/arXiv id)
Output: CONFIG.PATH.LITERATURE.BIB       (enriched; linked into the paper)
        CONFIG.PATH.LITERATURE.BIB_RECORD (scholar version, per-field sources)

Enrichment uses scholar's API-only metadata pipeline (DOI first; no PDF
download, no browser, no credentials). Reads and writes go through
scitex-io under @session, so clew records seed -> references.bib.
"""

import asyncio
import importlib.metadata
from datetime import UTC, datetime

import scitex_io as sio
import scitex_session as sess
from scitex_scholar.pipelines import ScholarPipelineMetadataParallel
from scitex_scholar.storage import BibTeXHandler

SCHOLAR_DIST = "scitex-scholar"
ENGINES_SUFFIX = "_engines"


def load_seed_papers(seed_path, handler):
    """Seed .bib -> (seed entries, Paper list), parsed by scitex-io."""
    seed_entries = sio.load(seed_path)
    papers = [handler.paper_from_bibtex_entry(entry) for entry in seed_entries]
    untitled = [e["key"] for e, p in zip(seed_entries, papers) if p is None]
    if untitled:
        raise ValueError(f"Seed entries without a title: {untitled}")
    return seed_entries, papers


def enrich_papers(papers, n_workers):
    """API-only metadata enrichment (DOI-first) via scholar's pipeline."""
    pipeline = ScholarPipelineMetadataParallel(num_workers=n_workers)
    return asyncio.run(pipeline.enrich_papers_async(papers))


def select_fields(entry, keep):
    """Entry restricted to the configured fields, in the configured order."""
    fields = entry["fields"]
    kept = {name: fields[name] for name in keep if fields.get(name)}
    return {"entry_type": entry["entry_type"], "key": entry["key"], "fields": kept}


def collect_field_sources(paper):
    """{section.field: [engines]} for every field scholar attributed."""
    sources = {}
    for section, values in paper.metadata.model_dump().items():
        if not isinstance(values, dict):
            continue
        for name, engines in values.items():
            if name.endswith(ENGINES_SUFFIX) and engines:
                sources[f"{section}.{name[: -len(ENGINES_SUFFIX)]}"] = list(engines)
    return sources


def describe_entry(seed_entry, bib_entry, full_entry, paper, note_fields):
    """Per-entry provenance: what scholar added and where it came from."""
    before = seed_entry["fields"]
    after = bib_entry["fields"]
    return {
        "key": bib_entry["key"],
        "doi": after.get("doi"),
        "added": [k for k in after if k not in before],
        "changed": [k for k in after if k in before and after[k] != before[k]],
        "sources": collect_field_sources(paper),
        **{name: full_entry["fields"].get(name) for name in note_fields},
    }


@sess.session
def main(
    CONFIG=sess.INJECTED,
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    """Enrich the seed bibliography into references.bib via scitex-scholar."""
    cfg = CONFIG.SCHOLAR
    paths = CONFIG.PATH.LITERATURE  # f-string leaves, eval() at each use
    handler = BibTeXHandler()

    seed_entries, papers = load_seed_papers(eval(paths.SEED_BIB), handler)
    logger.info(f"Seed: {len(papers)} entries from {eval(paths.SEED_BIB)}")

    enriched = enrich_papers(papers, cfg.N_WORKERS)
    full_entries = [handler.paper_to_bibtex_entry(p) for p in enriched]
    bib_entries = [select_fields(e, cfg.BIB_FIELDS) for e in full_entries]

    no_doi = [e["key"] for e in bib_entries if not e["fields"].get("doi")]
    if no_doi:
        logger.warning(f"No DOI resolved for: {no_doi}")
    sio.save(bib_entries, eval(paths.BIB), add_header=False, symlink_from_cwd=True)

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "tool": SCHOLAR_DIST,
        "tool_version": importlib.metadata.version(SCHOLAR_DIST),
        "api": "scitex_scholar.pipelines.ScholarPipelineMetadataParallel",
        "seed": eval(paths.SEED_BIB),
        "output": eval(paths.BIB),
        "bib_fields": list(cfg.BIB_FIELDS),
        "entries": [
            describe_entry(s, b, f, p, cfg.NOTE_FIELDS)
            for s, b, f, p in zip(seed_entries, bib_entries, full_entries, enriched)
        ],
    }
    sio.save(record, eval(paths.BIB_RECORD), symlink_from_cwd=True)
    logger.success(f"Saved {len(bib_entries)} entries -> {eval(paths.BIB)}")
    return 0


if __name__ == "__main__":
    main()

# EOF
