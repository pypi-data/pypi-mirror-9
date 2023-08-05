# Python RESTful API Asyncronous Logging Handler with Loggly Support
A simple logging handler for python that will send any logging events out to a
RESTful API using HTTP POST requests. Fully asyncronuous using requests-futures,
tested for Python 2 & 3, and has support for Loggly.

## Installation
pip install restapi-logging-handler

## Usage
Import whichever module(s) you need:
```
from restapi_logging_handler import RestApiHandler
from restapi_logging_handler import LogglyHandler
```

### RESTful API Usage
Set your Python logging handler to send logs to a REST-ful API
```
logger = logging.getLogger(__name__)
restapiHandler = RestApiHandler('http://my.restfulapi.com/endpoint/')
logger.addHandler(restapiHandler)
logger.setLevel(logging.INFO)
logger.info("Send this to my RESTful API")
```

By default, it sends the log data as a JSON object. You can currently change
that to send text instead.
```
restapiHandler = RestApiHandler('http://my.restfulapi.com/endpoint/', 'text')
```

### Loggly Usage
Set your Python logging handler to send logs out to your Loggly account. The
handler collects logs in a batch and sends them out every `interval` seconds.
After the interval passes, Loggly is sent all the logs collected. There are
`max_attempts` attempts to send the logs before the internal handleError() method
and an exception are thrown.
####Parameters
- custom_token: The LogglyHandler takes as its first argument the custom token given to you
when you sign up for a Loggly account.
- app_tags: The second argument can be a tag string,
or a list of tags to be associated with the log inside of Loggly.
- interval: defaults to 1 second
- max_attempts: defaults to 5 attempts

```
logglyHandler = LogglyHandler(
    custom_token='loggly-custom-key',
    app_tags=['tag1','tag2',...],
    interval=1.0,
    max_attemps=5
)
```


## Testing
Install tox and run it to test against Python 2 and 3.
```
sudo pip install nose
tox
```

## Forking
If you'd like to extend this to include more REST-ful API's than just Loggly,
send me a pull request!
