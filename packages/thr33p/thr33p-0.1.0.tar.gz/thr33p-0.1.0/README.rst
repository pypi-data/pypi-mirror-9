thr33p
======

.. image:: https://travis-ci.org/mayfieldrobotics/thr33p.svg
   :target: https://travis-ci.org/mayfieldrobotics/thr33p


.. image:: https://coveralls.io/repos/mayfieldrobotics/thr33p/badge.svg
   :target: https://coveralls.io/r/mayfieldrobotics/thr33p

Authenticating HTTP proxy for S3. Similar to these:

- `s3proxy <https://github.com/abustany/s3proxy>`_
- `s3-proxy-auth <https://github.com/samkeen/s3-proxy-auth>`_
- `ngx_aws_auth <https://github.com/anomalizer/ngx_aws_auth>`_

which *might* be better for you.

quickstart
==========

Create your config(s):

.. code:: bash

   $ cat > ~/.thr33p/config.py <<EOF
   import certifi
   
   http_pool_manager = {
      'cert_reqs': 'CERT_REQUIRED',
      'ca_certs': certifi.where(),
   }
    
   buckets =  {
      r'~.+-at-bernies': {
         'creds': {
            'access_key_id': 'EXAMPLE',
            'secret_access_key': 'EXAMPLEKEY',
         },
      }
   }
   EOF
   $ cat > ~/.thr33p/gunicorn.py <<EOF
   import os
   
   workers = 1
   
   backlog = 1024
   
   worker_class = 'gevent'
   
   loglevel = 'info'
   
   proc_name = 'thr33p'
   
   def post_fork(server, worker):
       import thr33p
   
       config_path = os.path.abspath(os.path.join(__file__, '..', 'config.py'))
       thr33p.init(config_path)
   
   EOF

and run it with `docker <https://registry.hub.docker.com/u/mayfieldrobotics/thr33p/>`_:

.. code:: bash

   $ sudo docker run -p 5000:8000 -v $HOME/.thr33p/:/etc/thr33p/ mayfieldrobotics/thr33p:latest --config=/etc/thr33p/gunicorn.py
   $ curl http://127.0.0.1:5000/dead-1.jpeg --header "Host:weekend-at-bernies.s3.amazonaws.com" -vvv

or ghetto dev style:

.. code:: bash

   $ mkvirtualenv thr33p
   (thr33p)$ pip install thr33p
   (thr33p)$ thr33p -d -p 5000 ~/.thr33p/config.py &
   (thr33p)$ curl http://127.0.0.1:5000/dead-1.jpeg --header "Host:weekend-at-bernies.s3.amazonaws.com" -vvv

config
======

Just a python file like e.g. this:

.. code:: python

   import os
   
   import certifi
   
   
   # passed to `urllib3.PoolManager`
   http_pool_manager = {
      'cert_reqs': 'CERT_REQUIRED',
      'ca_certs': certifi.where(),
   }
    
   buckets =  {
      # authenticates buckets matching literal "wake-at-bernies" using temporary iam-role creds
      r'wake-at-bernies': {
         'creds': None
      }
      
      # authenticates buckets matching literal "evening-at-bernies" using env creds
      r'evening-at-bernies': {
         'creds': {
            'access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
            'secret_access_key':os.environ['AWS_SECRET_ACCESS_KEY'],
         }
      }
      
      # authenticates buckets matching regex ".+-at-bernies" using baked creds
      r'~.+-at-bernies': {
         'creds': {
            'access_key_id': 'EXAMPLE',
            'secret_access_key': 'EXAMPLEKEY',
         },
      }
   }

dev
===

Get it:

.. code:: bash

   $ git clone git@github.com:mayfieldrobotics/thr33p.git 
   $ cd thr33p
   $ pip install -e .[tests]
   
   
test it:

.. code:: bash

   $ py.test tests/ --cov thr33p.py
   
and build docker images:

.. code:: bash

   $ sudo docker build -t {your-account}/thr33p .

release
=======

All is well:

.. code:: bash

   $ py.test tests/ --cov thr33p.py

so update ``__version__`` in:

- ``thr33p.py``

tag it (travis will publish it to `pypi <https://pypi.python.org/pypi/thr33p/>`_):

.. code:: bash

   $ git commit -am "release v{version}"
   $ git tag -a v{version} -m "release v{version}"
   $ git push --tags

and register the tag with `docker <https://registry.hub.docker.com/u/mayfieldrobotics/thr33p/>`_ so others can just:

.. code:: bash

   $ sudo docker pull mayfieldrobotics/thr33p:{version}
