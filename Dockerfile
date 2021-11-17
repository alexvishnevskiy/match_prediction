FROM python:3.9.7

WORKDIR /match-prediction

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
#download driver for selenium
RUN bash download_driver.sh
#insert data to database
#replace on_init function to main.py
RUN python3 match-prediction/db/on_init.py

CMD ["python3", "match-prediction/main.py"]