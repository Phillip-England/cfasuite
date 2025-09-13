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
```

3. Provide .env variables in `./env`:
```bash
SQLITE_ABSOLUTE_PATH= ## where you want your sqlite.db to exist
ADMIN_USER_ID=99999999 ## a random number (preferable 1000000+)
ADMIN_USERNAME=someusername ## a username for the admin user
ADMIN_PASSWORD=somepassword ## a password for the admin user
```

4. Init a virtual env
```bash
uv venv
```

5. Install deps:
```bash
uv pip install -r requirements.txt
```

## Running

```bash
uv run uvicorn main:app --reload
```
