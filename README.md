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
ADMIN_ID=99999999 ## a random number (preferable 1000000+)
ADMIN_USERNAME=someusername ## a username for the admin user
ADMIN_PASSWORD=somepassword ## a password for the admin user
TBOT_KEY=some_key_required_to_use_bot_endpoints  ## choose carefully
## *inserts env varibles for groupme bots*
```

4. Init a virtual env
```bash
uv venv
```

5. Install deps:
```bash
uv sync
```

## Running

```bash
uv run uvicorn main:app --reload
## or 'make run'
```
