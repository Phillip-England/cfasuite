
run:
	uv run uvicorn main:app --reload

install:
	uv pip install -r requirements.txt

format:
	uv run black .; uv run isort .;

bday:
	uv run python ./birthday_bot.py

tw:
	tailwindcss -i "./static/input.css" -o "./static/output.css" --watch