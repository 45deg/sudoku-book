UV_CACHE_DIR ?= .uv-cache
UV := UV_CACHE_DIR=$(UV_CACHE_DIR) uv
PYTHON := $(UV) run --frozen python
WORKSPACE_NODE ?= /Users/zkr/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
WORKSPACE_NODE_MODULES ?= /Users/zkr/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules

SPHINXBUILD := $(UV) run --frozen sphinx-build
SPHINXOPTS ?= -W --keep-going

.PHONY: generate references outputs test rst svg render serve check

generate: references outputs

references:
	$(PYTHON) tools/build_all_references.py

outputs:
	python3 tools/generate_outputs.py
	python3 examples/02-prolog/generate_outputs.py
	$(PYTHON) examples/03-minikanren/generate_outputs.py
	python3 examples/04-constraint-programming/generate_outputs.py
	python3 examples/05-exact-cover/generate_outputs.py
	$(PYTHON) examples/06-sat/generate_outputs.py
	$(PYTHON) examples/07-smt/generate_outputs.py
	$(PYTHON) examples/08-integer-programming/generate_outputs.py
	$(PYTHON) examples/09-asp/generate_outputs.py
	$(PYTHON) examples/10-bdd-model-counting/generate_outputs.py
	python3 examples/11-model-checking/generate_outputs.py
	$(PYTHON) examples/12-qubo/generate_outputs.py
	$(PYTHON) examples/13-iterative-projection/generate_outputs.py
	python3 examples/14-factor-graph/generate_outputs.py
	$(PYTHON) examples/15-groebner-basis/generate_outputs.py

test:
	python3 -m unittest discover -s examples/01-backtracking -p 'test_*.py' -v
	python3 -m unittest discover -s examples/02-prolog -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/03-minikanren -p 'test_*.py' -v
	python3 -m unittest discover -s examples/04-constraint-programming -p 'test_*.py' -v
	python3 -m unittest discover -s examples/05-exact-cover -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/06-sat -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/07-smt -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/08-integer-programming -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/09-asp -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/10-bdd-model-counting -p 'test_*.py' -v
	python3 -m unittest discover -s examples/11-model-checking -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/12-qubo -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/13-iterative-projection -p 'test_*.py' -v
	python3 -m unittest discover -s examples/14-factor-graph -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/15-groebner-basis -p 'test_*.py' -v

rst:
	$(SPHINXBUILD) $(SPHINXOPTS) -E -b dummy . build/dummy

svg:
	xmllint --noout figures/*/*.svg
	NODE_PATH=$(WORKSPACE_NODE_MODULES) $(WORKSPACE_NODE) tools/check_svg_collisions.mjs .

render:
	$(SPHINXBUILD) $(SPHINXOPTS) -b html . build/html

serve: render
	python3 -m http.server 8000 --directory build/html

check:
	$(PYTHON) tools/build_all_references.py --check
	python3 tools/generate_outputs.py --check
	python3 examples/02-prolog/generate_outputs.py --check
	$(PYTHON) examples/03-minikanren/generate_outputs.py --check
	python3 examples/04-constraint-programming/generate_outputs.py --check
	python3 examples/05-exact-cover/generate_outputs.py --check
	$(PYTHON) examples/06-sat/generate_outputs.py --check
	$(PYTHON) examples/07-smt/generate_outputs.py --check
	$(PYTHON) examples/08-integer-programming/generate_outputs.py --check
	$(PYTHON) examples/09-asp/generate_outputs.py --check
	$(PYTHON) examples/10-bdd-model-counting/generate_outputs.py --check
	python3 examples/11-model-checking/generate_outputs.py --check
	$(PYTHON) examples/12-qubo/generate_outputs.py --check
	$(PYTHON) examples/13-iterative-projection/generate_outputs.py --check
	python3 examples/14-factor-graph/generate_outputs.py --check
	$(PYTHON) examples/15-groebner-basis/generate_outputs.py --check
	python3 -m unittest discover -s examples/01-backtracking -p 'test_*.py' -v
	python3 -m unittest discover -s examples/02-prolog -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/03-minikanren -p 'test_*.py' -v
	python3 -m unittest discover -s examples/04-constraint-programming -p 'test_*.py' -v
	python3 -m unittest discover -s examples/05-exact-cover -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/06-sat -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/07-smt -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/08-integer-programming -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/09-asp -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/10-bdd-model-counting -p 'test_*.py' -v
	python3 -m unittest discover -s examples/11-model-checking -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/12-qubo -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/13-iterative-projection -p 'test_*.py' -v
	python3 -m unittest discover -s examples/14-factor-graph -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s examples/15-groebner-basis -p 'test_*.py' -v
	xmllint --noout figures/*/*.svg
	NODE_PATH=$(WORKSPACE_NODE_MODULES) $(WORKSPACE_NODE) tools/check_svg_collisions.mjs .
	$(SPHINXBUILD) $(SPHINXOPTS) -E -b dummy . build/dummy
	$(SPHINXBUILD) $(SPHINXOPTS) -b html . build/html
