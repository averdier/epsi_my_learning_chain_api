FROM python:3

ADD ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./config.py /
ADD ./runserver.py /
ADD ./wsgi.py /
ADD ./app /app/
ADD ./utils /utils/