FROM python:3.8.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /srv/email_client_backend
WORKDIR /srv/email_client_backend
COPY requirements.txt /srv/email_client_backend/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /srv/email_client_backend/