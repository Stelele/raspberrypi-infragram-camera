VENV=venv/bin/activate
PIP=./venv/bin/pip

$(VENV): requirements.txt
	python3 -m venv venv
	$(PIP) install -r requirements.txt
	
clean:
	rm -rf src/__pycache__ venv
	find . -name "*.rgb" -type f -delete
	find . -name "*.jpg" -type f -delete
	find . -name "*.png" -type f -delete