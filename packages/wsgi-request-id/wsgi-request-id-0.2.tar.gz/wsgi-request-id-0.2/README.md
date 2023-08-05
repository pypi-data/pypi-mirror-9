# wsgi-request-id

Make Request IDs available to your app, and also send one back to the client.

![](https://travis-ci.org/rhyselsmore/wsgi-request-id.svg)

## Usage

So simple.

```python
from somewhere import my_wsgi_app
import wsgi_request_id

app = wsgi_request_id.init_app(my_wsgi_app)
```

## Testing:

- use [tox](https://pypi.python.org/pypi/tox).

```bash
$ pip install tox
$ tox
```

- This takes care of py.test and all the other craziness.

## Contributing:

send me pull requests & doritos.
