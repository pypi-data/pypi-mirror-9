flask-endpoint
==============

![Build Image](https://travis-ci.org/rhyselsmore/flask-endpoint.svg?branch=master)

Adaption of Flask Blueprints to form 'Endpoints', with a focus on the path and method of a resource.

Class based views didn't cut it for me, so this is what I arrived at.

Go from this:

```
>>> blueprint = Blueprint('users', __name__, url_prefix='/users')
>>> @blueprint.route('/<string:user_id>', method=['DELETE'])
```

to this:

```
>>> endpoint = Endpoint('users', '/users', __name__)
>>> @endpoint.delete('/<string:user_id>')
```

Makes sense for my purposes, and I can still include per-route decorators, which is where classed based views fell down for me. This makes an incredible amount of sense in a HTTP API implementation where you need fine-grained control. For example, in the event that you want to implement a 'lockdown' of your API, you can include a specific decorator for 'changing' endpoints.

```
>>> @endpoint.post()
>>> @lockdown(severity=2)
```

# Installation

```
$ pip install flask-endpoint
```

Or if you prefer `easy-install`:

```
$ alias easy_install="pip install $1"
$ easy_install flask-redis
```

# Configuration

None (really!). Instead of running the following:

```
>>> from flask import Blueprint
```

just run:

```
>>> from flask_endpoint import Endpoint
```

and configure:

```
>>> endpoint = Endpoint('users', '/users', __name__)
>>> @endpoint.post()
>>> @endpoint.post('/url')
>>> @endpoint.get()
>>> @endpoint.get('/url')
```

The package supports all of the methods available to flask (GET/POST/PUT/PATCH/DELETE/OPTIONS/HEAD).

All of the standard blueprint optional arguments will be passed through (sans url-prefix), which makes this fairly easy to adopt.

When it comes time to register them, do as you would a Blueprint:

```
>>> app.register_blueprint(endpoint)
```

# Contribution

1. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug. There is a Contributor Friendly tag for issues that should be ideal for people who are not very familiar with the codebase yet.
2. Fork [the repository](https://github.com/rhyselsmore/flask-endpoint) on Github to start making your changes to the **master** branch (or branch off of it).
3. Write a test which shows that the bug was fixed or that the feature works as expected.
4. Send a pull request and bug the maintainer until it gets merged and published.
