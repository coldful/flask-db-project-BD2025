# Olympics Flask App

Small Flask application to browse the `Olympics.db` SQLite database. Includes table views, detail pages with related data, a sidebar overview, canned SQL questions, and a search/custom SQL page.

## Requirements

- Python 3
- `pip install Flask`

## Configure database

`db_Olympics_app/db.py` points to `Olympics.db` in the same folder. If you move the database, update `DB_FILE` accordingly. You can sanity‑check connectivity with:

```
python test_db_connection.py ATHLETE
```

## Run the server

From `db_Olympics_app/`:

```
python server.py
```

By default it starts on `http://localhost:9000`. Open that URL in a browser.

## Main routes

- `/` – landing page
- `/athletes/`, `/teams/`, `/sports/`, `/olympics/`, `/events/` – list views (with detail pages per record)
- `/search` – quick filters and a custom SQL (SELECT only) runner
- `/questions` – prebuilt SQL queries in `questions/`

## Structure

- `app.py` – Flask endpoints and query logic
- `db.py` – SQLite connector
- `templates/` – Jinja templates for pages and tables
- `static/style.css` – layout and styling
- `questions/` – canned SQL files loaded by `/questions`
- `test_db_connection.py` – quick DB connectivity check

## Notes

- Only `SELECT` is allowed in the custom SQL form for safety.
- Related tables on detail pages show links to the corresponding entities.
