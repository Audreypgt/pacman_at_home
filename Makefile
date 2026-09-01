NAME = pacman

# .python_version only works with pyenv, so the file was never used,
# we need to choose our python version here, when creating the venv
P3 = python3.11

run:
	@source pacman_venv/bin/activate \
	&& $(P3) pac_man.py config.json

install:
	@$(P3) -m venv pacman_venv
	@source pacman_venv/bin/activate \
	&& pip install --upgrade pip \
	&& pip install -r requirements.txt

debug:
	@source pacman_venv/bin/activate \
	&& python -m pdb pac_man.py

venv-clean:
	@if [ -r "pacman_venv" ]; then \
		rm -r pacman_venv; \
    fi

clean:
	@if [ -r "pacman/__pycache__" ]; then \
		rm -r ./pacman/__pycache__; \
    fi

	@if [ -r "__pycache__" ]; then \
		rm -r ./__pycache__; \
    fi

	@if [ -r ".mypy_cache" ]; then \
		rm -r ./.mypy_cache; \
    fi


fclean: clean venv-clean

lint:
	@source pacman_venv/bin/activate \
	&& flake8 parsing.py menu.py pac_man.py ghosts.py pacgums.py pacwoman.py \
	&& python -m mypy parsing.py menu.py pac_man.py ghosts.py pacgums.py pacwoman.py \
	--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	@source pacman_venv/bin/activate \
	&& flake8 parsing.py menu.py pac_man.py ghosts.py pacgums.py pacwoman.py \
	&& python -m mypy parsing.py menu.py pac_man.py ghosts.py pacgums.py pacwoman.py --strict

# build:
# 	python -m build