## Configuration

File *`bot_config.py`* should be in *`./app`* directory.

### Example of bot_config.py

```python
TOKEN # Bot token
API_URL # Url of chess server
DB_PATH # Absolute path to database file (sqlite)
REDIS_CONF = { # Configuration of redis storage
    "host": "localhost",
    "port": 6379,
    "prefix": ...
}
REDIS_URL # Url of redis database

GOD_MODE = False # Prevent checking move position
```

[REDIS_CONF options](https://docs.aiogram.dev/en/latest/dispatcher/fsm.html#aiogram.contrib.fsm_storage.redis.RedisStorage2)

-----

## Notes

If you're using app inside docker container, there should be several differences in *`bot_config.py`* file:

- **`DB_PATH`** should be `"/db/{DB_NAME}"`;
- **`REDIS_CONF.port`** should be `6379`.

-----

## Docker

### Build image

```bash
docker build -t {name} --build-arg CONFIG_PATH={path} .
```

If you want to have different config files for development and production, you can put another *`bot_config.py`* file to *`./.production`* directory and specify path in *`CONFIG_PATH`* build argument. This file will be used in your docker image.

### Run container

```bash
docker run -it -v {volume_with_database}:/db [IMAGE] {options}
```

To see options, run:
```bash
python main.py --help
```

-----