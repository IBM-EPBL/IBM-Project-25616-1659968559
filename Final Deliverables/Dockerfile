# syntax=docker/dockerfile:1

FROM python:3.10.7
WORKDIR /run
ADD . /run
COPY requirements.txt /run
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000
CMD ["python","run.py"]