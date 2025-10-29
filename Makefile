
run:
	uv run uvicorn main:app --reload

install:
	uv pip install -r requirements.txt

format:
	uv run black .; uv run isort .;