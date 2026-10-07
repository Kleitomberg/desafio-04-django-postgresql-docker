FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install -r ./requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD [ "gunicorn", "-b 0.0.0.0:8000", "config.wsgi:application" ]