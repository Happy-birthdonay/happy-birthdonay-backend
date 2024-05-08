FROM python:3.10

ENV APP_HOME /app

ENV PORT 8000

WORKDIR $APP_HOME

COPY . ./

RUN pip3 install --no-cache-dir -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 run:app
