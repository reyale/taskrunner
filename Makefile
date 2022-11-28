all:
	pytest ./test.py
	flake8 ./bin/* ./lib/*
