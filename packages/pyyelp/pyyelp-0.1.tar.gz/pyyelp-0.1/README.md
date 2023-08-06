Pyyelp
=======

Pyyelp is a python wrapper for the **Yelp API v2**

`Yelp API v2 docs <https://www.yelp.com/developers/documentation>`

Requires
-------
- oauth2

Fast install
-------
```
pip install pyyelp
```

- Add the following in **settings.py** or .bash_profile

```python
YELP_API_CONSUMER_KEY={{ CONSUMER_KEY }}
YELP_API_CONSUMER_SECRET={{ CONSUMER_SECRET }}
YELP_API_TOKEN={{ TOKEN }}
YELP_API_TOKEN_SECRET={{ SECRET_TOKEN }}
```

Fast example
-------

```python
from pyyelp import Yelp

yelp = Yelp()
search_result = yelp.search(term="foo store")
```

Examples
-------
1. **Search** Example
```python
from pyyelp import Yelp

yelp = Yelp()
search_result = yelp.search(term="Don Quixote's Restaurant", location="Santa Cruz, California", limit=25)
```

2. **Business** Example
```python
from pyyelp import Yelp

yelp = Yelp()
business_result = yelp.get_business_by_id("taqueria-los-gallos-newark")
```

3. **Phone** Example
```python
from pyyelp import Yelp

yelp = Yelp()
phone_result = yelp.search_by_phone_number("1234567890")
```

TODO
-------
- Errors
- Proper Testing

Contribute
-------
1. Fork the `repo <https://github.com/motte/python-yelp>`_
2. Test the code thoroughly
3. Code with `pep8 <http://www.python.org/dev/peps/pep-0008/>`_ rules
4. Pull request

Tests
-------
Unit test setup to come.
