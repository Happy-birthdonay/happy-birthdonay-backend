FROM python:3.11.7

ENV APP_HOME /app

ENV PORT 8000

WORKDIR $APP_HOME

COPY . ./

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install build
RUN python3 -m build
