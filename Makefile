all:
	python3 -m pytest ./test.py
	flake8 --ignore=E501,E722 ./bin/*.py ./lib/*.py
