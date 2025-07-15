# UMSC Donate

A Django-based donation platform for UMSC.

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate     # On Unix/MacOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Development Server

```bash
python manage.py runserver
```

The server will be available at http://127.0.0.1:8000/

## Project Structure

- `web/` - Main application directory
- `umsc_donate/` - Project configuration directory
- `static/` - Static files (CSS, JavaScript, images)
- `media/` - User-uploaded files
- `staticfiles/` - Collected static files (created after running collectstatic)

## Features

- [List main features here]

## Contributing

[Add contribution guidelines here] # icuc_donate
