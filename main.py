from flask import Flask, jsonify, render_template
from scripts.scrapping import get_data
import numpy as np

app = Flask(__name__)


# @app.route("/")
# def print_results():
#     X = np.load('X_val.npy')
#     result = predict(X, 'base_model.joblib').tolist()
#     return jsonify(
#         price = result
#     )
@app.route("/")
def home():
    data = get_data('https://www.xscores.com/soccer/england/premier-league')
    return render_template('home.html', data = data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port = 8080)