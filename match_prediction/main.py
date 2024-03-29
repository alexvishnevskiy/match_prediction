from airflow.scripts.get_logger import get_logger
from flask import Flask, jsonify, render_template
from airflow.scripts.db.ops import retrieve
from waitress import serve


app = Flask(__name__)

def choose_color(data: list):
    color_mapping = {
        "green": "#19FF06",
        "red": "#FF2D00",
        "yellow": "#FFF006"
    }

    for i in range(len(data)):
        probs = data[i][-3:]
        colors = ["", "", ""]
        max_indx = max(range(len(probs)), key=probs.__getitem__)
        min_indx = min(range(len(probs)), key=probs.__getitem__)
        # max -> green, middle -> yellow, min -> red
        colors[max_indx] = color_mapping["green"]
        colors[min_indx] = color_mapping["red"]
        colors[(set(range(3))-set([max_indx, min_indx])).pop()] = color_mapping["yellow"]

        data[i] = list(data[i])
        data[i].extend(colors)
    return data

@app.route("/")
def home():
    logger = get_logger(__file__)
    
    try:
        condition = """
        referee IS NOT NULL
        and status = 'SCHEDULED'
        """
        data = retrieve(condition = condition)
        data = choose_color(data)
    except Exception as e:
        logger.exception(e)
    return render_template('home.html', data = data)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5005)
    #app.run(port=5005, host = "0.0.0.0", debug=False)