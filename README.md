# spa-fastapi-htmx-alpinejs
Simple login page on Single Page Application approach using FastAPI + HTMX + AlpineJS

## Get Started
```bash
# start creating venv
python3.13 -m venv .venv

# activate venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# make a .venv file with content
JWT_KEY = "<your 64bits key>"
JWT_ALGORITHM = "HS256"
EXPIRATION_TIME = 3600
DATABASE_URL = "postgresql://my_site:master@localhost/my_site"
# NOTE: change user/password/dbname in migration files as you need

# start dev
fastapi dev main.py --host 0.0.0.0
```
