VENV=venv/bin/activate
PIP=./venv/bin/pip

$(VENV): requirements.txt
	python3 -m venv venv
	$(PIP) install -r requirements.txt

run:
	python src/app.py
	
clean:
	rm -rf src/__pycache__ venv
	find . -wholename "./output/**/*.rgb" -type f -delete
	find . -wholename "./output/**/*.jpg" -type f -delete
	find . -wholename "./output/**/*.png" -type f -delete
	find . -wholename "./output/**/*.h264" -type f -delete
	find . -wholename "./output/**/*.mp4" -type f -delete