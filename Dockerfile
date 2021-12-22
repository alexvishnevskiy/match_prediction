FROM python:3.9.7
WORKDIR /match_prediction

ENV AIRFLOW_HOME=/match_prediction/match_prediction/airflow
ENV PYTHONPATH "${PYTHONPATH}:${AIRFLOW_HOME}"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

#initialize table and run
CMD /bin/bash -c "python3 match_prediction/airflow/scripts/db/on_init.py; \
      python3 match_prediction/airflow/scripts/train.py; \
      python3 match_prediction/airflow/scripts/predict.py; \
      python3 match_prediction/main.py"