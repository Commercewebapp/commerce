FROM python:3

WORKDIR /root/

COPY requirements.txt /root/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /root/
