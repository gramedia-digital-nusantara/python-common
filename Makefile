build:
	python setup.py sdist bdist_wheel

clean:
	pip uninstall --yes gdn-python-common
	rm -fR .cache/ .eggs/ build/ dist/ *.egg-info MANIFEST

local-install: clean build
	pip install dist/*.whl

test: local-install
	pytest

