all: setup

setup:
	python3 -m venv venv
	

clean:
	rm -rf src/__pycache__
	find . -name "*.rgb" -type f -delete
	find . -name "*.jpg" -type f -delete
	find . -name "*.png" -type f -delete