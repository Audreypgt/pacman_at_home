NAME = pacman

P3 = python3

run: install
	@source pacman_venv/bin/activate \
	&& $(P3) pac-man.py config.json

install:
	@$(P3) -m venv pacman_venv
	@source pacman_venv/bin/activate \
	&& pip install --quiet --upgrade pip \
	&& pip install --quiet -r requirements.txt

debug: install
	@source pacman_venv/bin/activate \
	&& python -m pdb pac-man.py

clean:
	@if [ -r "pacman_venv" ]; then \
		rm -r pacman_venv; \
    fi

# 	@if [ -r "mazegen/__pycache__" ]; then \
# 		rm -r ./mazegen/__pycache__; \
#     fi

	@if [ -r "__pycache__" ]; then \
		rm -r ./__pycache__; \
    fi

	@if [ -r ".mypy_cache" ]; then \
		rm -r ./.mypy_cache; \
    fi

lint: install
# 	@source pacman_venv/bin/activate \
# 	&& flake8 parsing.py menu.py pac-man.py mazegen/maze.py mazegen/__init__.py setup.py \
# 	&& mypy parsing.py menu.py pac-man.py mazegen/maze.py mazegen/__init__.py setup.py \
# 	--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
# 	--check-untyped-defs

lint-strict: install
# 	@source pacman_venv/bin/activate \
# 	&& flake8 parsing.py menu.py pac-man.py mazegen/maze.py mazegen/__init__.py setup.py \
# 	&& mypy parsing.py menu.py pac-man.py mazegen/maze.py mazegen/__init__.py setup.py --strict

# build:
# 	python -m build