FROM python:3.9 as builder

WORKDIR /src
COPY . .

RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python3","-u","/src/main.py"]