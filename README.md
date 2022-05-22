## Configuration

File `bot_config.py` should be in `./app` directory.

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
```

[REDIS_CONF options](https://docs.aiogram.dev/en/latest/dispatcher/fsm.html#aiogram.contrib.fsm_storage.redis.RedisStorage2)

-----