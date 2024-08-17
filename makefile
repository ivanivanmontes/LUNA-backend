# Makefile

# Default target to run the FastAPI app
run:
	uvicorn main:app --reload

# Target to install dependencies
install:
	pip install -r requirements.txt
