FROM python:3.11

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r /app/requirements.txt

COPY ./src .

EXPOSE 3000

CMD ["python", "app_ws.py"]