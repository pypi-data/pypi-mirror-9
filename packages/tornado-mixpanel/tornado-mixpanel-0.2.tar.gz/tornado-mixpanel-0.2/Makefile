clear:
	-rm -fRv build data dist docs libs *.egg-info
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

deps:
	mkdir -v libs
	pip install -t libs -r requirements.txt

publish:
	python setup.py register
	python setup.py sdist upload