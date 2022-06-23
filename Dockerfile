FROM python:3.10-alpine

ARG CONFIG_PATH=./app/bot_config.py

WORKDIR /bot

COPY . ./

COPY ${CONFIG_PATH} ./app/bot_config.py

RUN pip3 install -r requirements.txt

VOLUME /db

ENTRYPOINT ["python3", "main.py"]

CMD ["--loglevel", "WARNING"]
