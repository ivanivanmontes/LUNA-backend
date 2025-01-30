# Makefile


# Target to open the IDE + activate virtual environment
open:
	./open_project.sh
# Default target to run the FastAPI app
run_local:
	uvicorn app.main:app --reload

# Target to install dependencies
install:
	pip install -r requirements.txt

run_global:
	uvicorn app.main:app --host 0.0.0.0 --port 8000
