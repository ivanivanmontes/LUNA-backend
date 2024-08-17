# Makefile


# Target to open the IDE + activate virtual environment
open:
	./open_project.sh
# Default target to run the FastAPI app
run:
	uvicorn main:app --reload

# Target to install dependencies
install:
	pip install -r requirements.txt
