all: setup

setup:
	python3 -m venv venv
	

clean:
	find . -name "*.rgb" -type f -delete
	find . -name "*.jpg" -type f -delete