# CMPUT302-HighFidelityProject3

## Install and run

Clone the repository and open a terminal in the project folder:

```bash
git clone <repository-url>
cd <cloned-repo-folder>
```

If you already have the repository downloaded, make sure your terminal is opened in this same folder before running the commands below.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Apply the database migrations and start the Django development server:

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the app

## Quick checklist

1. Clone the repo.
2. `cd` into the cloned project folder.
3. Create and activate `.venv`.
4. Run `pip install -r requirements.txt`.
5. Run `python manage.py migrate`.
6. Run `python manage.py runserver`.
7. Visit `http://127.0.0.1:8000/`.
