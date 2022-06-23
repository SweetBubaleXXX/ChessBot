FROM python:3.10-alpine

WORKDIR /bot

COPY . ./

RUN pip3 install -r requirements.txt

VOLUME /db

ENTRYPOINT ["python3", "main.py"]

CMD ["--loglevel", "WARNING"]
