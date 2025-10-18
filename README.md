# ReqSense

A Flask web application.

## Setup

1. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/app.py
   ```

4. Open browser: http://localhost:5000

## Project Structure

```
ReqSense/
├── src/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── routes/             # Route handlers
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── tests/                  # Test files
├── docs/                   # Documentation
└── requirements.txt        # Dependencies
```

## Development

Run tests:
```bash
pytest tests/
```
