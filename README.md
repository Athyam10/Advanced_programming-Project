# MediaTrack

MediaTrack is a lightweight desktop + backend application for managing media metadata (books, films, magazines and other media).  
It includes a Flask backend that stores the library in a JSON file and a PyQt5 desktop frontend that communicates with the API.


# Features

- Add / Edit / Delete media items
- Category filtering (book, film, magazine, other)
- Exact-name search
- Track availability and expected return dates
- JSON-backed storage (library.json) — easy to inspect and portable
- Automated tests for backend (pytest) and frontend (pytest-qt)


# Project structure

Project/
├── Library-backend/
│ ├── app/
│ │ ├── init.py
│ │ ├── routes.py
│ │ ├── storage.py
│ ├── library.json # persisted storage (generated at runtime)
│ ├── manage.py
│ └── tests/
│ └── test_api.py
├── Library_Frontend/
│ ├── main.py
│ └── tests/
│ └── test_gui.py
├── README.md
└── requirements.txt


# Quickstart (development)

These instructions assume you have Python 3.10+ installed and will use a virtual environment.


# Setup (macOS / Linux)

```bash
cd Project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


            # Setup (Windows PowerShell)

cd Project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt


              # Running the backend

cd Library-backend
# if using manage.py as the entrypoint:
export FLASK_APP=manage.py        # Windows PowerShell: $env:FLASK_APP='manage.py'
flask run
# or:
python manage.py


            # Running the frontend

cd Library_Frontend
python main.py


        # If your backend is on a different host/port, open main.py and change:

API_BASE = "http://127.0.0.1:5000/api"
