import sqlite3
import pandas as pd

# File locations
DB_FILE = "Olympics.db"
EXCEL_FILE = "Olympics.xlsx"

# Column mapping from Excel to DB fields
COLUMN_MAP = {
    # ATHLETE
    "athlete_id": "ID",
    "athlete_name": "Name",
    "sex": "Sex",
    "height": "Height",
    "weight": "Weight",

    # TEAM
    "team_id": "team_id",
    "team_name": "Team",
    "noc": "NOC",

    # SPORT
    "sport_id": "sport_id",
    "sport_name": "Sport",

    # OLYMPICS
    "olympics_id": "olympics_id",
    "olympics_name": "Games",
    "year": "Year",
    "season": "Season",
    "city": "City",

    # EVENT
    "event_id": "event_id",
    "event_name": "Event",

    # PARTICIPATED_IN
    "age": "Age",
    "medal": "Medal",
}


def clean(value):
    """
    Normalize values read from Excel.

    - Converts NaN or empty values to None
    - Strips leading/trailing whitespace
    - Returns a cleaned string or None
    """
    if value is None or (isinstance(value, float) and pd.isna(value)) or pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def to_int_safe(value):
    """
    Safely convert a value to integer.

    Returns None if conversion is not possible.
    """
    value = clean(value)
    if value is None:
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def to_float_safe(value):
    """
    Safely convert a value to float.

    Returns None if conversion is not possible.
    """
    value = clean(value)
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def ensure_schema(cursor):
    """
    Create all database tables and indexes if they do not already exist.

    This function defines the relational schema corresponding
    to the ER model and enforces primary and foreign key constraints.
    """
    schema = """
    CREATE TABLE IF NOT EXISTS TEAM (
        team_id INTEGER PRIMARY KEY,
        name    TEXT NOT NULL,
        noc     TEXT
    );

    CREATE TABLE IF NOT EXISTS ATHLETE (
        athlete_id INTEGER PRIMARY KEY,
        name       TEXT NOT NULL,
        sex        TEXT,
        height     REAL,
        weight     REAL
    );

    CREATE TABLE IF NOT EXISTS SPORT (
        sport_id INTEGER PRIMARY KEY,
        name     TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS OLYMPICS (
        olympics_id INTEGER PRIMARY KEY,
        name        TEXT,
        year        INTEGER,
        season      TEXT,
        city        TEXT
    );

    CREATE TABLE IF NOT EXISTS EVENT (
        event_id    INTEGER PRIMARY KEY,
        name        TEXT NOT NULL,
        sport_id    INTEGER NOT NULL,
        olympics_id INTEGER NOT NULL,
        FOREIGN KEY (sport_id) REFERENCES SPORT(sport_id),
        FOREIGN KEY (olympics_id) REFERENCES OLYMPICS(olympics_id)
    );

    CREATE TABLE IF NOT EXISTS IN_THE_TEAM (
        athlete_id INTEGER NOT NULL,
        team_id    INTEGER NOT NULL,
        PRIMARY KEY (athlete_id, team_id),
        FOREIGN KEY (athlete_id) REFERENCES ATHLETE(athlete_id),
        FOREIGN KEY (team_id)    REFERENCES TEAM(team_id)
    );

    CREATE TABLE IF NOT EXISTS PARTICIPATED_IN (
        athlete_id INTEGER NOT NULL,
        event_id   INTEGER NOT NULL,
        age        INTEGER,
        medal      TEXT,
        PRIMARY KEY (athlete_id, event_id),
        FOREIGN KEY (athlete_id) REFERENCES ATHLETE(athlete_id),
        FOREIGN KEY (event_id)   REFERENCES EVENT(event_id)
    );

    CREATE INDEX IF NOT EXISTS idx_event_sport    ON EVENT(sport_id);
    CREATE INDEX IF NOT EXISTS idx_event_olympics ON EVENT(olympics_id);
    CREATE INDEX IF NOT EXISTS idx_it_team        ON IN_THE_TEAM(team_id);
    CREATE INDEX IF NOT EXISTS idx_pi_event       ON PARTICIPATED_IN(event_id);
    """
    cursor.executescript(schema)


def make_id_resolver(cursor, table, pk_column, unique_columns):
    """
    Create a resolver function for a table primary key.

    The resolver:
    - checks whether a record with the given unique key already exists
    - returns its primary key if found
    - otherwise inserts a new record and generates a new primary key

    Parameters:
        cursor (sqlite3.Cursor): Active database cursor
        table (str): Table name
        pk_column (str): Primary key column name
        unique_columns (list[str]): Columns defining uniqueness

    Returns:
        function: A resolver function that accepts unique key values
    """
    cursor.execute(f"SELECT COALESCE(MAX({pk_column}), 0) FROM {table}")
    next_pk = cursor.fetchone()[0] + 1
    cache = {}

    def resolve(*keys):
        """
        Resolve or generate a primary key for a given unique key.
        """
        nonlocal next_pk
        key_tuple = tuple(keys)
        if any(v is None for v in key_tuple):
            return None
        if key_tuple in cache:
            return cache[key_tuple]

        where_clause = " AND ".join([f"{col} = ?" for col in unique_columns])
        cursor.execute(
            f"SELECT {pk_column} FROM {table} WHERE {where_clause} LIMIT 1",
            key_tuple,
        )
        found = cursor.fetchone()
        if found:
            cache[key_tuple] = found[0]
            return found[0]

        placeholders = ",".join(["?"] * (1 + len(unique_columns)))
        insert_cols = [pk_column] + list(unique_columns)
        cursor.execute(
            f"INSERT INTO {table}({','.join(insert_cols)}) VALUES ({placeholders})",
            (next_pk, *key_tuple),
        )
        cache[key_tuple] = next_pk
        next_pk += 1
        return cache[key_tuple]

    return resolve


# ---------- Data import ----------
sheet = pd.read_excel(EXCEL_FILE)

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

ensure_schema(cursor)
connection.commit()

team_pk     = make_id_resolver(cursor, "TEAM", "team_id", ["name", "noc"])
sport_pk    = make_id_resolver(cursor, "SPORT", "sport_id", ["name"])
olympics_pk = make_id_resolver(
    cursor, "OLYMPICS", "olympics_id", ["year", "season", "city", "name"]
)
event_pk    = make_id_resolver(
    cursor, "EVENT", "event_id", ["name", "sport_id", "olympics_id"]
)
athlete_pk  = make_id_resolver(
    cursor, "ATHLETE", "athlete_id", ["name", "sex"]
)

for _, row in sheet.iterrows():
    # ATHLETE
    athlete_id = to_int_safe(row.get(COLUMN_MAP["athlete_id"])) if COLUMN_MAP.get("athlete_id") in sheet.columns else None
    athlete_name = clean(row.get(COLUMN_MAP["athlete_name"]))
    gender = clean(row.get(COLUMN_MAP["sex"]))
    height_val = to_float_safe(row.get(COLUMN_MAP["height"])) if COLUMN_MAP.get("height") in sheet.columns else None
    weight_val = to_float_safe(row.get(COLUMN_MAP["weight"])) if COLUMN_MAP.get("weight") in sheet.columns else None

    if athlete_id is None:
        athlete_id = athlete_pk(athlete_name, gender)

    if athlete_id is not None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO ATHLETE(athlete_id, name, sex, height, weight)
            VALUES (?, ?, ?, ?, ?)
            """,
            (athlete_id, athlete_name, gender, height_val, weight_val),
        )

    # TEAM
    team_id = to_int_safe(row.get(COLUMN_MAP["team_id"])) if COLUMN_MAP.get("team_id") in sheet.columns else None
    team_name = clean(row.get(COLUMN_MAP["team_name"]))
    noc_val = clean(row.get(COLUMN_MAP["noc"]))

    if team_id is None:
        team_id = team_pk(team_name, noc_val)

    if team_id is not None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO TEAM(team_id, name, noc)
            VALUES (?, ?, ?)
            """,
            (team_id, team_name, noc_val),
        )

    if athlete_id is not None and team_id is not None:
        cursor.execute(
            "INSERT OR IGNORE INTO IN_THE_TEAM(athlete_id, team_id) VALUES (?, ?)",
            (athlete_id, team_id),
        )

    # SPORT
    sport_id = to_int_safe(row.get(COLUMN_MAP["sport_id"])) if COLUMN_MAP.get("sport_id") in sheet.columns else None
    sport_name = clean(row.get(COLUMN_MAP["sport_name"]))

    if sport_id is None:
        sport_id = sport_pk(sport_name)

    if sport_id is not None:
        cursor.execute(
            "INSERT OR IGNORE INTO SPORT(sport_id, name) VALUES (?, ?)",
            (sport_id, sport_name),
        )

    # OLYMPICS
    olympics_id = to_int_safe(row.get(COLUMN_MAP["olympics_id"])) if COLUMN_MAP.get("olympics_id") in sheet.columns else None
    olympics_name = clean(row.get(COLUMN_MAP["olympics_name"]))
    year_val = to_int_safe(row.get(COLUMN_MAP["year"]))
    season_val = clean(row.get(COLUMN_MAP["season"]))
    city_val = clean(row.get(COLUMN_MAP["city"]))

    if olympics_id is None:
        olympics_id = olympics_pk(year_val, season_val, city_val, olympics_name)

    if olympics_id is not None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO OLYMPICS(olympics_id, name, year, season, city)
            VALUES (?, ?, ?, ?, ?)
            """,
            (olympics_id, olympics_name, year_val, season_val, city_val),
        )

    # EVENT
    event_id = to_int_safe(row.get(COLUMN_MAP["event_id"])) if COLUMN_MAP.get("event_id") in sheet.columns else None
    event_name = clean(row.get(COLUMN_MAP["event_name"]))

    if event_id is None:
        event_id = event_pk(event_name, sport_id, olympics_id)

    if event_id is not None and sport_id is not None and olympics_id is not None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO EVENT(event_id, name, sport_id, olympics_id)
            VALUES (?, ?, ?, ?)
            """,
            (event_id, event_name, sport_id, olympics_id),
        )

    # PARTICIPATED_IN
    age_val = to_int_safe(row.get(COLUMN_MAP["age"])) if COLUMN_MAP.get("age") in sheet.columns else None
    medal_val = clean(row.get(COLUMN_MAP["medal"])) if COLUMN_MAP.get("medal") in sheet.columns else None

    if athlete_id is not None and event_id is not None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO PARTICIPATED_IN(athlete_id, event_id, age, medal)
            VALUES (?, ?, ?, ?)
            """,
            (athlete_id, event_id, age_val, medal_val),
        )

connection.commit()
connection.close()
print("Import into Olympics.db completed successfully!")
