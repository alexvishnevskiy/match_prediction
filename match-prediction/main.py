from flask import Flask, jsonify, render_template
from db.ops import retrieve
from db.on_init import get_init_table
import time


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
    path = 'https://www.xscores.com/soccer/england/premier-league'
    get_init_table(path)
    app.run(debug=True, host="0.0.0.0", port = 8889)