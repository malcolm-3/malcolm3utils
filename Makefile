SHELL=/bin/zsh

ACTIVATE:=if [ "$$VIRTUAL_ENV" != "$$PWD/venv" ]; then . venv/bin/activate; fi

venv:
	virtualenv --prompt "malcolm3utils-venv" venv || echo "You may need to pip install virtualenv"

git-is-clean:
	@output=$$(git status --porcelain 2>&1) && [ -z "$$output" ] || (echo "git is not clean"; echo $$output; exit 1)

pre-commit-check:
	$(ACTIVATE); poetry run pre-commit run --all-files


version-patch: git-is-clean pre-commit-check
	$(ACTIVATE); poetry version patch; poetry run kacl-cli release patch -m
	$(ACTIVATE); V=`poetry run kacl-cli current`; git commit -a -m "Release $$V"; git tag "v$$V"
	$(ACTIVATE); poetry build

version-minor: git-is-clean pre-commit-check
	$(ACTIVATE); poetry version minor; poetry run kacl-cli release minor -m
	$(ACTIVATE); V=`poetry run kacl-cli current`; git commit -a -m "Release $$V"; git tag "v$$V"
	$(ACTIVATE); poetry build

version-major: git-is-clean pre-commit-check
	$(ACTIVATE); poetry version major; poetry run kacl-cli release major -m
	$(ACTIVATE); V=`poetry run kacl-cli current`; git commit -a -m "Release $$V"; git tag "v$$V"
	$(ACTIVATE); poetry build

test:
	$(ACTIVATE); poetry run pytest

docs:
	$(ACTIVATE); mkdos build
