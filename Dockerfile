FROM python:3.9.7

WORKDIR /match-prediction

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "match-prediction/main.py"]