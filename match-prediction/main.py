from flask import Flask, jsonify, render_template
from db import ops


app = Flask(__name__)

@app.route("/")
def home():
    condition = """
    referee IS NOT NULL
    and bet_1x IS NOT NULL
    and played = 0
    """
    data = ops.retrieve(condition)
    return render_template('home.html', data = data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port = 8889)