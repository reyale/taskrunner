all:
	python3 -m pytest ./test.py
	flake8 --ignore=E501,E722 ./bin/*.py ./lib/*.py

clean:
	find ./var/unittest/ -type f -not -name '*.md' -delete	
	find ./var/ -type f -not -name '*.md' -delete	
