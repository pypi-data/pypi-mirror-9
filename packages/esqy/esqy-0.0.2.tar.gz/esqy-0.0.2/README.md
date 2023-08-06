# esqy

Run elasticsearch queries from json file, like in examples folder.

# Install

	pip install esqy

or install from source

	python setup.py install

# Examples

	esqy examples/health.json

	esqy -h localhost:9200 examples/health.json

	esqy -h user:passwd@localhost:9200 examples/health.json

	cat examples/health.json | esqy
