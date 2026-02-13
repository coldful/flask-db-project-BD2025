import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os
import sqlite3
from flask import Flask, render_template, request, url_for

import db


APP = Flask(__name__)
APP.url_map.strict_slashes = False

# -------------------------
# DB PATH
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Olympics.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def link(endpoint, pk_name, pk_value, label=None):
    """Return an HTML anchor to a detail endpoint."""
    href = url_for(endpoint, **{pk_name: pk_value})
    return f'<a href="{href}">{label or pk_value}</a>'


# -------------------------
# HOME
# -------------------------
@APP.route('/')
def index():
    return render_template('index.html')


@APP.before_request
def ensure_db_connected():
    # Keep DB connection alive for request handlers
    if 'conn' not in db.DB:
        db.connect()


@APP.context_processor
def inject_sidebar_data():
    """
    Provide sidebar menu data: table counts and links.
    Keeps the left pane static while the right pane swaps content.
    """
    tables = [
        ("athletes_list", "ATHLETE", "ATHLETE"),
        ("teams_list", "TEAM", "TEAM"),
        ("sports_list", "SPORT", "SPORT"),
        ("olympics_list", "OLYMPICS", "OLYMPICS"),
        ("events_list", "EVENT", "EVENT"),
    ]
    counts = []
    try:
        with get_conn() as conn:
            for endpoint, table, label in tables:
                total = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
                counts.append(
                    {
                        "endpoint": endpoint,
                        "label": label,
                        "table": table,
                        "count": total,
                    }
                )
    except Exception:
        # If DB is unavailable, keep sidebar empty rather than breaking the page
        counts = []

    return {"sidebar_tables": counts}


# =========================================================
# TABLE ENDPOINTS
# =========================================================

@APP.route('/athletes/')
def athletes_list():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT athlete_id, name, sex
            FROM ATHLETE
            ORDER BY athlete_id;
            """
        ).fetchall()

    rows = [
        {
            "athlete_id": r['athlete_id'],
            "name": link('athlete_detail', 'athlete_id', r['athlete_id'], r['name']),
            "sex": r['sex'],
        }
        for r in rows
    ]

    return render_template(
        'table_list.html',
        table_name='ATHLETE',
        pk_name='athlete_id',
        rows=rows,
        detail_endpoint='athlete_detail'
    )


@APP.route('/athletes/<int:athlete_id>/')
def athlete_detail(athlete_id):
    with get_conn() as conn:
        record = conn.execute(
            "SELECT * FROM ATHLETE WHERE athlete_id = ?;",
            (athlete_id,)
        ).fetchone()

        teams = conn.execute(
            """
            SELECT t.team_id, t.name, t.noc
            FROM IN_THE_TEAM it
            JOIN TEAM t ON t.team_id = it.team_id
            WHERE it.athlete_id = ?
            ORDER BY t.name;
            """,
            (athlete_id,)
        ).fetchall()

        participations = conn.execute(
            """
            SELECT
                e.event_id,
                e.name AS event_name,
                s.sport_id,
                s.name AS sport,
                o.year,
                o.season,
                o.city,
                o.olympics_id,
                pi.medal
            FROM PARTICIPATED_IN pi
            JOIN EVENT e      ON e.event_id = pi.event_id
            JOIN SPORT s      ON s.sport_id = e.sport_id
            JOIN OLYMPICS o   ON o.olympics_id = e.olympics_id
            WHERE pi.athlete_id = ?
            ORDER BY o.year, s.name, e.name;
            """,
            (athlete_id,)
        ).fetchall()

    teams_rows = [
        {
            "team_id": link('team_detail', 'team_id', t['team_id']),
            "name": link('team_detail', 'team_id', t['team_id'], t['name']),
            "noc": t['noc'],
        }
        for t in teams
    ]

    participations_rows = [
        {
            "event_id": link('event_detail', 'event_id', p['event_id']),
            "event_name": link('event_detail', 'event_id', p['event_id'], p['event_name']),
            "sport": link('sport_detail', 'sport_id', p['sport_id'], p['sport']),
            "games": link('olympics_detail', 'olympics_id', p['olympics_id'], p['year']),
            "year": p['year'],
            "season": p['season'],
            "city": p['city'],
            "medal": p['medal'],
        }
        for p in participations
    ]

    related_sections = [
        {"title": "Teams", "rows": teams_rows},
        {"title": "Participations", "rows": participations_rows}
    ]

    return render_template(
        'table_detail.html',
        table_name='ATHLETE',
        record=record,
        back_endpoint='athletes_list',
        related_sections=related_sections
    )


@APP.route('/teams/')
def teams_list():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT team_id, name, noc
            FROM TEAM
            ORDER BY team_id;
            """
        ).fetchall()

    rows = [
        {
            "team_id": r['team_id'],
            "name": link('team_detail', 'team_id', r['team_id'], r['name']),
            "noc": r['noc'],
        }
        for r in rows
    ]

    return render_template(
        'table_list.html',
        table_name='TEAM',
        pk_name='team_id',
        rows=rows,
        detail_endpoint='team_detail'
    )


@APP.route('/teams/<int:team_id>/')
def team_detail(team_id):
    with get_conn() as conn:
        record = conn.execute(
            "SELECT * FROM TEAM WHERE team_id = ?;",
            (team_id,)
        ).fetchone()

        athletes = conn.execute(
            """
            SELECT a.athlete_id, a.name, a.sex
            FROM IN_THE_TEAM it
            JOIN ATHLETE a ON a.athlete_id = it.athlete_id
            WHERE it.team_id = ?
            ORDER BY a.name;
            """,
            (team_id,)
        ).fetchall()

        medal_breakdown = conn.execute(
            """
            SELECT COALESCE(pi.medal, 'No medal') AS medal, COUNT(*) AS count
            FROM PARTICIPATED_IN pi
            JOIN IN_THE_TEAM it ON it.athlete_id = pi.athlete_id
            WHERE it.team_id = ?
            GROUP BY medal
            ORDER BY count DESC;
            """,
            (team_id,)
        ).fetchall()

    athlete_rows = [
        {
            "athlete_id": link('athlete_detail', 'athlete_id', a['athlete_id']),
            "name": link('athlete_detail', 'athlete_id', a['athlete_id'], a['name']),
            "sex": a['sex'],
        }
        for a in athletes
    ]

    related_sections = [
        {"title": "Athletes", "rows": athlete_rows},
        {"title": "Medals by result", "rows": medal_breakdown}
    ]

    return render_template(
        'table_detail.html',
        table_name='TEAM',
        record=record,
        back_endpoint='teams_list',
        related_sections=related_sections
    )


@APP.route('/sports/')
def sports_list():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT sport_id, name
            FROM SPORT
            ORDER BY sport_id;
            """
        ).fetchall()

    rows = [
        {
            "sport_id": r['sport_id'],
            "name": link('sport_detail', 'sport_id', r['sport_id'], r['name']),
        }
        for r in rows
    ]

    return render_template(
        'table_list.html',
        table_name='SPORT',
        pk_name='sport_id',
        rows=rows,
        detail_endpoint='sport_detail'
    )


@APP.route('/sports/<int:sport_id>/')
def sport_detail(sport_id):
    with get_conn() as conn:
        record = conn.execute(
            "SELECT * FROM SPORT WHERE sport_id = ?;",
            (sport_id,)
        ).fetchone()

        events = conn.execute(
            """
            SELECT e.event_id, e.name AS event_name, o.year, o.season, o.city, o.olympics_id
            FROM EVENT e
            JOIN OLYMPICS o ON o.olympics_id = e.olympics_id
            WHERE e.sport_id = ?
            ORDER BY o.year, e.name;
            """,
            (sport_id,)
        ).fetchall()

    event_rows = [
        {
            "event_id": link('event_detail', 'event_id', e['event_id']),
            "event_name": link('event_detail', 'event_id', e['event_id'], e['event_name']),
            "games": link('olympics_detail', 'olympics_id', e['olympics_id'], e['year']),
            "year": e['year'],
            "season": e['season'],
            "city": e['city'],
        }
        for e in events
    ]

    related_sections = [{"title": "Events", "rows": event_rows}]

    return render_template(
        'table_detail.html',
        table_name='SPORT',
        record=record,
        back_endpoint='sports_list',
        related_sections=related_sections
    )


@APP.route('/olympics/')
def olympics_list():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT olympics_id, name, year, season, city
            FROM OLYMPICS
            ORDER BY year;
            """
        ).fetchall()

    rows = [
        {
            "olympics_id": r['olympics_id'],
            "name": link('olympics_detail', 'olympics_id', r['olympics_id'], r['name']),
            "year": r['year'],
            "season": r['season'],
            "city": r['city'],
        }
        for r in rows
    ]

    return render_template(
        'table_list.html',
        table_name='OLYMPICS',
        pk_name='olympics_id',
        rows=rows,
        detail_endpoint='olympics_detail'
    )


@APP.route('/olympics/<int:olympics_id>/')
def olympics_detail(olympics_id):
    with get_conn() as conn:
        record = conn.execute(
            "SELECT * FROM OLYMPICS WHERE olympics_id = ?;",
            (olympics_id,)
        ).fetchone()

        events = conn.execute(
            """
            SELECT e.event_id, e.name AS event_name, s.sport_id, s.name AS sport
            FROM EVENT e
            JOIN SPORT s ON s.sport_id = e.sport_id
            WHERE e.olympics_id = ?
            ORDER BY s.name, e.name;
            """,
            (olympics_id,)
        ).fetchall()

    event_rows = [
        {
            "event_id": link('event_detail', 'event_id', e['event_id']),
            "event_name": link('event_detail', 'event_id', e['event_id'], e['event_name']),
            "sport": link('sport_detail', 'sport_id', e['sport_id'], e['sport']),
        }
        for e in events
    ]

    related_sections = [{"title": "Events", "rows": event_rows}]

    return render_template(
        'table_detail.html',
        table_name='OLYMPICS',
        record=record,
        back_endpoint='olympics_list',
        related_sections=related_sections
    )


@APP.route('/events/')
def events_list():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                e.event_id,
                e.name AS event_name,
                s.sport_id,
                s.name AS sport,
                o.year,
                o.season,
                o.city,
                COUNT(pi.athlete_id) AS medalists
            FROM EVENT e
            JOIN SPORT s ON s.sport_id = e.sport_id
            JOIN OLYMPICS o ON o.olympics_id = e.olympics_id
            LEFT JOIN PARTICIPATED_IN pi ON pi.event_id = e.event_id
            GROUP BY e.event_id, e.name, s.name, o.year, o.season, o.city
            ORDER BY o.year, s.name, e.name;
            """
        ).fetchall()

    rows = [
        {
            "event_id": r['event_id'],
            "event_name": link('event_detail', 'event_id', r['event_id'], r['event_name']),
            "sport": link('sport_detail', 'sport_id', r['sport_id'], r['sport']),
            "year": r['year'],
            "season": r['season'],
            "city": r['city'],
            "medalists": r['medalists'],
        }
        for r in rows
    ]

    return render_template(
        'table_list.html',
        table_name='EVENT',
        pk_name='event_id',
        rows=rows,
        detail_endpoint='event_detail'
    )


@APP.route('/events/<int:event_id>/')
def event_detail(event_id):
    with get_conn() as conn:
        record = conn.execute(
            """
            SELECT
                e.event_id,
                e.name AS event_name,
                s.name AS sport,
                o.name AS games_name,
                o.year,
                o.season,
                o.city
            FROM EVENT e
            JOIN SPORT s ON s.sport_id = e.sport_id
            JOIN OLYMPICS o ON o.olympics_id = e.olympics_id
            WHERE e.event_id = ?;
            """,
            (event_id,)
        ).fetchone()

        medalists = conn.execute(
            """
            SELECT
                a.athlete_id,
                a.name AS athlete_name,
                a.sex,
                t.team_id,
                t.name AS team,
                pi.medal
            FROM PARTICIPATED_IN pi
            JOIN ATHLETE a ON a.athlete_id = pi.athlete_id
            LEFT JOIN IN_THE_TEAM it ON it.athlete_id = a.athlete_id
            LEFT JOIN TEAM t ON t.team_id = it.team_id
            WHERE pi.event_id = ?
            ORDER BY a.name;
            """,
            (event_id,)
        ).fetchall()

    medalist_rows = [
        {
            "athlete_id": link('athlete_detail', 'athlete_id', p['athlete_id']),
            "athlete_name": link('athlete_detail', 'athlete_id', p['athlete_id'], p['athlete_name']),
            "sex": p['sex'],
            "team": link('team_detail', 'team_id', p['team_id'], p['team']) if p['team_id'] else p['team'],
            "medal": p['medal'],
        }
        for p in medalists
    ]

    related_sections = [{"title": "Medalists", "rows": medalist_rows}]

    return render_template(
        'table_detail.html',
        table_name='EVENT',
        record=record,
        back_endpoint='events_list',
        related_sections=related_sections
    )


# =========================================================
# QUERIES (files inside ./questions)
# =========================================================

QUESTION_TEXTS = {
    1: 'Total number of athletes stored.',
    2: 'Top 10 teams by medal count.',
    3: 'How many events exist for each sport?',
    4: 'Average athlete height and weight grouped by sex.',
    5: 'Cities that have hosted the Olympics and how many times.',
    6: 'Events with the largest number of medalists (top 10).',
    7: 'Medal breakdown by sport (gold/silver/bronze).',
    8: 'Athletes with the highest medal counts (top 10).',
    9: 'Teams (NOC) that competed in the widest variety of sports (top 10).',
    10: 'Olympic host cities ordered by number of events held.',
    11: 'Average medalist age by sport (where age is known).',
    12: 'Medalist counts per Olympic games (top 10).'
}

SQL_FOLDER = os.path.join(os.path.dirname(__file__), 'questions')


def execute_query_from_file(file_number):
    sql_file_path = os.path.join(SQL_FOLDER, f"{file_number}.sql")

    if not os.path.exists(sql_file_path):
        return {"error": f"SQL file {file_number}.sql not found.", "query": "", "columns": [], "results": []}

    query = ""
    try:
        with open(sql_file_path, "r") as sql_file:
            query = sql_file.read()

        cursor = db.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return {"error": None, "query": query, "columns": columns, "results": results}

    except Exception as e:
        return {"error": str(e), "query": query, "columns": [], "results": []}


@APP.route('/questions')
def questions():
    sql_files = sorted(
        [f for f in os.listdir(SQL_FOLDER) if f.endswith('.sql')],
        key=lambda x: int(x.split('.')[0])
    )

    questions = []
    for f in sql_files:
        num = int(f.split('.')[0])
        questions.append({
            "num": num,
            "filename": f,
            "text": QUESTION_TEXTS.get(num, "Question without description")
        })

    return render_template('questions.html', questions=questions)


@APP.route('/query-result/<int:file_number>')
def query_result(file_number):
    data = execute_query_from_file(file_number)
    return render_template('query_result.html', file_number=file_number, **data)


@APP.route('/search', methods=['GET', 'POST'])
def search():
    """
    Simple search hub: quick filters + optional custom SELECT.
    """
    filter_type = request.values.get('filter_type')
    term = (request.values.get('term') or '').strip()
    custom_sql = request.values.get('custom_sql', '').strip()

    filter_result = {"columns": [], "rows": [], "error": None}
    custom_result = {"columns": [], "rows": [], "error": None, "query": custom_sql}

    if filter_type and term:
        try:
            with get_conn() as conn:
                if filter_type == 'athletes_name':
                    cursor = conn.execute(
                        """
                        SELECT athlete_id, name, sex
                        FROM ATHLETE
                        WHERE name LIKE ?
                        ORDER BY name
                        """,
                        (f"%{term}%",),
                    )
                elif filter_type == 'teams_noc':
                    cursor = conn.execute(
                        """
                        SELECT team_id, name, noc
                        FROM TEAM
                        WHERE noc LIKE ?
                        ORDER BY name
                        """,
                        (f"%{term}%",),
                    )
                elif filter_type == 'sports_name':
                    cursor = conn.execute(
                        """
                        SELECT sport_id, name
                        FROM SPORT
                        WHERE name LIKE ?
                        ORDER BY name
                        """,
                        (f"%{term}%",),
                    )
                elif filter_type == 'events_year':
                    cursor = conn.execute(
                        """
                        SELECT event_id, name AS event_name, year, season, city
                        FROM EVENT e
                        JOIN OLYMPICS o ON o.olympics_id = e.olympics_id
                        WHERE o.year = ?
                        ORDER BY event_name
                        """,
                        (term,),
                    )
                else:
                    cursor = None

                if cursor:
                    rows = cursor.fetchall()
                    filter_result["columns"] = [c[0] for c in cursor.description]
                    filter_result["rows"] = rows
        except Exception as exc:
            filter_result["error"] = str(exc)

    if custom_sql:
        try:
            normalized = custom_sql.strip().lower()
            if not normalized.startswith("select"):
                raise ValueError("Only SELECT queries are allowed.")
            cursor = db.execute(custom_sql)
            rows = cursor.fetchall()
            custom_result["columns"] = [c[0] for c in cursor.description] if cursor.description else []
            custom_result["rows"] = rows
        except Exception as exc:
            custom_result["error"] = str(exc)

    return render_template(
        'search.html',
        filter_result=filter_result,
        custom_result=custom_result,
        filter_type=filter_type or '',
        term=term,
        custom_sql=custom_sql,
    )
