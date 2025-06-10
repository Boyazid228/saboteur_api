# Saboteur API

This is an API built with Django, using Redis for caching/data storage and Uvicorn as the ASGI server.

## Requirements

- Python 3.8+
- Redis Server
- pip (Python package installer)
- Git

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/saboteur_api.git
cd saboteur_api

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start Redis server (must be installed beforehand)
redis-server

# 5. Run the application with Uvicorn
uvicorn saboteur_api.asgi:application --reload

## Documentation
 - Open the file [docs/docs.pdf] to view the documentation.
