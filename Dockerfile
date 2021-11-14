FROM python:3.9.7

WORKDIR /price-prediction

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN bash download_driver.sh

CMD ["python3", "main.py"]