# research-clew Makefile — clean-DAG dispatcher.
#
# IMPORTANT: do NOT set `SHELL := /bin/bash` here — that breaks
# @stx.session under make. The system /bin/sh is fine; the actual
# work happens inside python3 calls.
#
# Each recipe is one verb-named agent script. `make solve` runs the
# whole chain; `make verify` is the out-of-band schema check
# (plain python, NOT in the Clew DAG).

ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PY   := python3

.PHONY: all solve verify clean clean-clew help

all: solve verify

solve: clean-clew                                # AGENT — Clew-tracked
	$(PY) $(ROOT)/scripts/agent/01_load_data.py
	$(PY) $(ROOT)/scripts/agent/02_compute_stats.py
	$(PY) $(ROOT)/scripts/agent/03_register_claims.py

verify:                                          # VERIFIER — plain python, NOT in agent DAG
	$(PY) $(ROOT)/scripts/verify/check_schema.py

clean-clew:
	rm -f  $(ROOT)/.scitex/clew/db.sqlite
	rm -f  $(ROOT)/.scitex/clew/runtime/db.sqlite

clean: clean-clew
	find $(ROOT)/scripts -type d -name "*_out" -prune -exec rm -rf {} +
	rm -rf $(ROOT)/data/intermediate/* $(ROOT)/data/results/*
	touch  $(ROOT)/data/intermediate/.gitkeep $(ROOT)/data/results/.gitkeep

help:
	@echo "make solve    -- run the agent DAG (produces data/results/claims.json)"
	@echo "make verify   -- out-of-band schema check on claims.json"
	@echo "make clean    -- nuke generated artefacts (keep source)"
