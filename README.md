# CFA Suite
A web application with internal tools I use for my role at Chick-fil-A.

## Installation

1. clone the repo:
```bash
git clone https://github.com/phillip-england/cfasuite
cd cfasuite
```

2. Create a `.env`:
```bash
touch .env
cat <<EOF > ./cfasuite.env
SQLITE_ABSOLUTE_PATH=/path/to/you/sqlite.db
ADMIN_USER_ID=99999999
ADMIN_PASSWORD=somepassword
ADMIN_USERNAME=someusername
EOF
```

3. Install deps:
```bash
uv pip install -r requirements.txt ## or 'make install'
```

## Running

```bash
uv run uvicorn main:app --reload ## or 'make run'
```
