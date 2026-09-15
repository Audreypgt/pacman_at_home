NAME = pacman

P3 = python3

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

	@if [ -r "build_env" ]; then \
		rm -r build_env; \
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
	&& flake8 parsing.py game_controller.py pac_man.py ghosts.py pacgums.py pacwoman.py utils.py \
	&& mypy parsing.py game_controller.py pac_man.py ghosts.py pacgums.py pacwoman.py utils.py \
	--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	@source pacman_venv/bin/activate \
	&& flake8 parsing.py game_controller.py pac_man.py ghosts.py pacgums.py pacwoman.py utils.py \
	&& mypy parsing.py game_controller.py pac_man.py ghosts.py pacgums.py pacwoman.py utils.py --strict

build:
	@$(P3) -m venv build_env \
	&& source build_env/bin/activate \
	&& $(P3) -m pip install -r requirements.txt \
	&& $(P3) -m pip install pyinstaller \
	&& pyinstaller --onedir --clean --name "PacWoman" --add-data "sprites/*.png:sprites" pac_man.py

.PHONY:	run install debug venv-clean clean fclean lint lint-strict build
