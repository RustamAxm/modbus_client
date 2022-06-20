FROM python:3.8

LABEL maintainer="Rustam Akhmadullin"

USER root

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip

RUN pip install -r  requirements.txt


RUN wget https://github.com/contactless/modbus-utils/releases/download/1.2/modbus-utils_1.2_amd64.deb

RUN set -ex \
    && apt -qq update
RUN apt install -y libmodbus5
RUN dpkg -i ./modbus-utils_1.2_amd64.deb

CMD ["python3", "-u","main.py"]

