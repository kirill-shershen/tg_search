FROM python:3.9

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
		postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

ADD requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt coverage

COPY . /code/

WORKDIR /code/src
