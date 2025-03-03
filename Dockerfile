#FROM ubuntu:latest
#LABEL authors="Сергій"
#ENTRYPOINT ["top", "-b"]
FROM python

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]

