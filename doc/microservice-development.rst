
Development of eduID
====================

The eduID service is based on a collection of RESTish microservices that are
used by js front-end applications.

Development of microservices
----------------------------

EduID microservices are based on `Flask <http://flask.pocoo.org/>`_, and reside
in `github <https://github.com/SUNET/eduid-webapp/>`_, as Python packages
below `src/eduid_webapp/`.

The main modules that comprise an eduID microservice are as follows.

views.py
........

This module holds the views for the app. A flask Blueprint is instantiated in
this module, and the views are registered in this blueprint.

app.py
......

In this module there must be a function that takes as parameters a str name
for the app and a dict of settings, and returns a Flask application.

The settings param is there to be able to inject test settings in tests,
and is not used for production.

The initial eduID app is obtained in this module by the use of the
`init_eduid_app` function from `eduid_common.api.app`. This function returns
a Flask app with the following special properties:

**Authentication**

For any request, the app checks that it carries an authn token as a cookie,
and if not, redirects to the authentication service. Thhe logic for this is
implemented in `eduid_common.authn.middleware`.

**Configuration**

The app has an attribute `config` with all the configuration paramenters. These
parameters can be provided in several ways: in an ini file, in an etcd server,
and as mentioned above, as a dictionary when instantiating the app. The logic
for this is implemented in `eduid-common.config.parsers`.

Defaults for the configuration parameters common to all apps are kept in
`eduid_webapp.settings.common`. Overrides of these settings for specific apps,
and defaults for settings  that are specific for each app, are kept in a Python
module (for each app), at `eduid_webapp.<some_app>.settings.common`.

**Logging**

The app has a `logger` attribute that we can use to send information to
the logs.

**Database**

The app has a connection to the central user db in the attribute
`central_userdb`. This db is only used to read user data; to write user data
we must use dbs specific for each app, that sinchronize with the central db
through celery tasks. This attribute points to an instance of
`eduid_userdb.UserDB`, that provides methods to save data to and retrieve
data from the db, in the form of `eduid_userdb.User` objects.

On top of all this, each app can initialize its flask app with whatever covers
the specific needs of the particular microservice. The most common tasks are
registering the blueprint(s) instantiated in the `views.py` module, and
providing connections for the local dbs needed by the microservice, in the form
of proxies developed in `eduid_userdb`.

All manipulation of persistent data is made through the objects and db proxies
developed ineduid_userdb.

run.py
......

Instantiate the app with the init function in `app.py` and run it.

schemas.py, validators.py
.........................

For input validation and deserialization of form submissions from users we
use `marsmallow <http://marshmallow.readthedocs.io/en/latest/index.html>`_.
Schemas are kept in schemas.py and validators in validators.py (surprise).

This is not to be  confused with input sanitation, that is performed
transparently for any access to request data, and is implemented in
`eduid_common.api.request`.

Testing microservices
.....................

**MongoTestCase**

There is a test case defined in `eduid_userdb.testing.MongoTestCase` that
provides a connection to a temporary mongodb instance, and an interface to it
in a `amdb` attribute that points to an instance of `eduid_userdb.UserDB`.
This db comes preloaded with a couple of mock users defined in
`eduid_userdb.testing`.

**EduidAPITestCase**

There is a test case in `eduid_common.api.testing.EduidAPITestCase`. This test
case has temporary instances of redis (for sessions) and of mongodb, and an
`app` attribute pointing to an instance of a flask app.

Test cases extending this must implement an `load_app(self, config)` method
where they return the particular flask app to be tested, and can implement a
method `update_config(self, config)` where they can provide any needed
configuration params.

Sessions
........

The flask app returned by `init_eduid_app` has a custom session factory,
based on redis, implemented in `eduid_common.session.session`, and adapted for
flask in `eduid_common.api.session`. These sessions can be accesed as usual
in flask apps (in the `session` attribute of the app) and are shared by all
microservices, with the data kept in a central redis service.

Each request must carry a cookie with an authentication token, which is an
encrypted key for the session data in redis. If it doesn't, the request is
redirected to the authn service. If it does, the app retrieves the session
data from redis and holds it in `session`.

In the session there is a key `user_eppn` with the eppn of the logged in user.
If we need the logged in user in some view, we use the `require_dashboard_user`
decorator from `eduid_common.api.decorators`, that provides a `user` argument
to the decorated view.

Development of front end applications
-------------------------------------

Front end apps are developed with `React <https://facebook.github.io/react/>`_,
and reside in `eduid-html/react`.

The development environment has a few pieces:

 * npm. Node package manager, to manage dependencies and metadata. Configured
   in `react/package.json`. npm is also the main entry point to managing the
   dev environment, and defines the following scripts:

   * `npm start` builds the bundle for development, and watches the files for
     changes to rebundle them.
   * `npm test` runs the tests.
   * `npm run build` makes a bundle for production use. This bundle is kept
     under version control, at least until the build process is integrated
     in puppet.

 * webpack is a module bundler, whose main purpose is to bundle JavaScript
   files for usage in a browser. There are 2 config files for webpack, one
   `react/webpack.config.js` for development and testing, and another
   `react/webpack.prod.config.js` for production bundles.

 * babel is a transpiler, used by webpack to transpile react and es6 sources
   into the es5 bundles that can be interpreted by any browser.

 * karma is a test runner, configured in `react/karma.conf.js`. It is
   configured to use webpack to prepare the sources for the tests, mocha as a
   real browser driver (to run the tests in firefox, chrome, etc.), and
   istambul/isparta for code coverage. The tests are written using enzyme, a
   testing framework for react. The tests  are kept in `react/src/tests`, and
   must have a filename ending in `-test.js`. There is a file
   `react/src/test.webpack.js` that acts as entry point for all tests for the
   runner.

The react components are kept in `react/components`, and are used (inserted
in the DOM) by scripts kept in `react/src` (e.g., `personal-data.js`.

For the internalization of the react apps we use react-intl and
babel-plugin-react-intl, that hooks message extraction with the webpack build
process. The messages are stored in `react/i18n-messages`, and the translations
are stored in `react/l10n/<lang>.js`. Unfortunately this framework does not
follow the gettext standard, and thus could not be used with transifex.

Docker
------

Each microservice is deployed in a docker container. There is a base Dockerfile
for microservices at `eduid-webapp/docker/`. The Dockerfile for each
microservice is kept in a subdirectory in the eduid-dockerfiles repository, and
they basically extend the base Dockerfile to inject a script to configure and
run the app within a gunicorn wsgi server (e.g. see
eduid-dockerfiles/eduid-personal/start.sh`.) Any new distribution dependency for
new apps are added to the base Dockerfile at `eduid-webapp/docker/setup.sh`.

Container configurations are kept in the eduid-developer repository. The
configuration for the services is provided by a etcd container, and is kept at
`eduid-developer/etcd/conf.yaml`.

The configuration for the containers is managed by docker-compose and is kept
in `eduid-developer/eduid/compose.yml`.

To update the images for the docker environment we run, from the root of the
eduid-developer repo::

  docker-compose -f eduid/compose.yml pull

The docker environment is started by a script in `eduid-developer/start.sh`.