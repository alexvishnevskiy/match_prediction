from flask import Flask, jsonify, render_template
from airflow.scripts.db.ops import retrieve


app = Flask(__name__)

@app.route("/")
def home():
    condition = """
    referee IS NOT NULL
    and bet_1x IS NOT NULL
    and played = 0
    """
    data = retrieve(condition)
    return render_template('home.html', data = data)


if __name__ == "__main__":
    app.run()