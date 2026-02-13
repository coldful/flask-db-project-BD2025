# Olympics Database Web Application

A Flask-based web application for exploring and querying an SQLite database of Olympic Games data.

---

## Features

The application provides:

- Table list views
- Detail pages with related entities
- Sidebar overview with record counts
- Predefined analytical SQL queries
- Safe custom SQL execution (SELECT-only)

---

## Table Browsing

Browse and inspect the following entities:

- Athletes
- Teams
- Sports
- Olympic Games
- Events

Each detail page includes related data such as:

- Athlete participations
- Team medal statistics
- Event medalists

---

## Search & Filtering

The `/search` page allows:

### Quick filtering by:

- Athlete name
- Team NOC
- Sport name
- Olympic year

### Custom SQL queries

Users can execute custom SQL queries with restrictions:

- Only `SELECT` queries are allowed
- Dangerous SQL keywords are blocked
- A result limit is automatically applied

---

## Prebuilt SQL Questions

The `/questions` page executes analytical SQL queries stored in:

```
db_Olympics_app/questions/
```

---

## Tech Stack

- Python 3
- Flask
- SQLite
- HTML + CSS

---

## Project Structure

<img width="494" height="252" alt="image" src="https://github.com/user-attachments/assets/e25ed825-57d9-4912-8f7e-50470e53c0e8" />

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/flask-db-project-BD2025.git
cd flask-db-project-BD2025/db_Olympics_app
```

Install dependencies:

```bash
pip install Flask
```

---

## Running the Application

From inside `db_Olympics_app/`:

```bash
python server.py
```

The application runs by default at:

```
http://localhost:9000
```

Open this URL in your browser.

---

## Database Configuration

The database file is expected at:

```
db_Olympics_app/Olympics.db
```

If you move the database file, update the path inside:

```
db.py
```

You can test database connectivity with:

```bash
python test_db_connection.py ATHLETE
```

---

## Purpose

This project was developed as a university database systems assignment.

It demonstrates:

- Relational database design
- SQL query development
- Flask backend architecture
- Safe query execution patterns
- Dynamic template rendering with Jinja
