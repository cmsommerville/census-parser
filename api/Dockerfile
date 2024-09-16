# Pull official base image and fixing to AMD Architecture
FROM python:3.11
ENV PYTHONUNBUFFERED 1

RUN apt-get install sqlite3
WORKDIR /api

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install gunicorn
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]