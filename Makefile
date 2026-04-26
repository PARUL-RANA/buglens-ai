# BugLens AI — Makefile
# Requires GNU Make. On Windows use Git Bash, WSL, or winget install GnuWin32.Make

.PHONY: setup data train run test check all

setup:
	python -m venv venv && venv/bin/pip install -r requirements.txt

data:
	python generate_data.py

train:
	python train_model.py

run:
	python app.py

test:
	python test_buglens.py

check:
	python model_check.py

all: data train run
