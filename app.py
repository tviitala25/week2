import os

import pymysql
from flask import Flask, make_response, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Nginx provides info about the original connection and the application subpath. (/week2).
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_prefix=1,
)


def increment_counter():
    connection = pymysql.connect(
        unix_socket="/run/mysqld/mysqld.sock",
        user="week2app",
        password=os.environ["DB_PASSWORD"],
        database="week2",
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE counter SET visits = visits + 1 WHERE id = 1"
            )
            cursor.execute(
                "SELECT visits FROM counter WHERE id = 1"
            )
            visits = cursor.fetchone()[0]
        connection.commit()
        return visits
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.route("/")
def front_page():
    visits = increment_counter()
    response = make_response(render_template("index.html", visits=visits))
    # The browser must not display the old counter value from the cache.
    response.headers["Cache-Control"] = "no-store"
    return response
