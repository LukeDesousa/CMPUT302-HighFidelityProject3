# CMPUT302-HighFidelityProject3

## Django setup

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the project:

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the home page and `http://127.0.0.1:8000/admin/` for the admin site.
