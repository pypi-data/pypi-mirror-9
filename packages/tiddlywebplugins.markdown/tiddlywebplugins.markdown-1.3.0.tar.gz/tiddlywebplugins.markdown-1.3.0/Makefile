.PHONY: test dist upload

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r *.egg-info || true

test: clean
	py.test -x --tb=short test

dist: test
	python setup.py sdist

release: clean pypi

pypi: test
	python setup.py sdist upload
