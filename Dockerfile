FROM tiangolo/uwsgi-nginx-flask:python3.6

WORKDIR /app

RUN apt update
RUN apt install -y xvfb
RUN apt install -y wkhtmltopdf

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app
