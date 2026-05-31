# research-minimal Makefile -- clean-DAG dispatcher.
# IMPORTANT: do NOT set `SHELL := /bin/bash` (breaks @stx.session under make).

ROOT  := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PY    := python3
AGENT := $(ROOT)/scripts/agent
VERIFY := $(ROOT)/scripts/verify

.PHONY: help solve verify-claims clean clean-clew

solve: clean-clew                                # AGENT - Clew-tracked
	$(PY) $(AGENT)/01_load_data.py
	$(PY) $(AGENT)/02_compute_stats.py
	$(PY) $(AGENT)/03_register_claims.py

verify-claims:                                   # VERIFIER - plain python, NOT in agent DAG
	$(PY) $(VERIFY)/check_schema.py

clean-clew:
	rm -f $(ROOT)/.scitex/clew/db.sqlite $(ROOT)/.scitex/clew/runtime/db.sqlite 2>/dev/null || true

clean: clean-clew
	find $(ROOT) -type d -name "*_out" -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(ROOT)/output $(ROOT)/data/intermediate/* $(ROOT)/data/results/*
	touch  $(ROOT)/data/intermediate/.gitkeep $(ROOT)/data/results/.gitkeep

help:
	@echo "make solve          -- run the agent DAG (produces data/results/claims.json)"
	@echo "make verify-claims  -- out-of-band schema check"
	@echo "make clean          -- nuke generated artefacts"
