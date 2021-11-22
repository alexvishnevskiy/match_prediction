from flask import Flask, jsonify, render_template
from db.ops import retrieve
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
    app.run()