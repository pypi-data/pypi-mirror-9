# coding=utf-8
import threading

try:
    from sqlalchemy.engine.url import make_url
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.schema import MetaData
except ImportError:
    raise ImportError(
        'Unable to load the sqlalchemy package.'
        ' `SQLAlchemy-Wrapper` needs the SQLAlchemy library to run.'
        ' You can get download it from http://www.sqlalchemy.org/'
        ' If you\'ve already installed SQLAlchemy, then make sure you have '
        ' it in your PYTHONPATH.')

from .helpers import (
    _create_scoped_session, _include_sqlalchemy,
    BaseQuery, Model, EngineConnector
)


class SQLAlchemy(object):
    """This class is used to instantiate a SQLAlchemy connection to
    a database.

    .. sourcecode:: python

        db = SQLAlchemy(_uri_to_database_)

    The class also provides access to all the SQLAlchemy
    functions from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.
    So you can declare models like this:

    .. sourcecode:: python

        class User(db.Model):
            login = db.Column(db.String(80), unique=True)
            passw_hash = db.Column(db.String(80))

    In a web application you need to call ``db.session.remove()``
    after each response, and ``db.session.rollback()`` if an error occurs.

    No need to do it If your application object has an ``after_request``
    and ``on_exception`` decorators, just pass your application object
    at creation:

    .. sourcecode:: python

        app = Flask(__name__)
        db = SQLAlchemy('sqlite://', app=app)

    or later:

    .. sourcecode:: python

        db = SQLAlchemy()

        app = Flask(__name__)
        db.init_app(app)

    .. admonition:: Check types carefully

       Don't perform type or ``isinstance`` checks against ``db.Table``, which
       emulates ``Table`` behavior but is not a class. ``db.Table`` exposes the
       ``Table`` interface, but is a function which allows omission of metadata.

    """

    def __init__(self, uri='sqlite://', app=None, echo=False,
                 pool_size=None, pool_timeout=None, pool_recycle=None,
                 convert_unicode=True, query_cls=BaseQuery):
        self.uri = uri
        self.info = make_url(uri)
        self.options = self._cleanup_options(
            echo=echo,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            convert_unicode=convert_unicode,
        )

        self.connector = None
        self._engine_lock = threading.Lock()
        self.session = _create_scoped_session(self, query_cls=query_cls)

        self.Model = declarative_base(cls=Model, name='Model')
        self.Model.db = self
        self.Model.query = self.session.query

        if app is not None:
            self.init_app(app)

        _include_sqlalchemy(self)

    def _cleanup_options(self, **kwargs):
        options = dict([
            (key, val)
            for key, val in kwargs.items()
            if val is not None
        ])
        return self.apply_driver_hacks(options)

    def apply_driver_hacks(self, options):
        """This method is called before engine creation and used to inject
        driver specific hacks into the options.

        The options parameter is a dictionary of keyword arguments that will
        then be used to call the :mod:`sqlalchemy.create_engine()` function.

        The default implementation provides some saner defaults for things
        like pool sizes for MySQL and sqlite.
        """
        if self.info.drivername == 'mysql':
            self.info.query.setdefault('charset', 'utf8')
            options.setdefault('pool_size', 10)
            options.setdefault('pool_recycle', 7200)

        elif self.info.drivername == 'sqlite':
            no_pool = options.get('pool_size') == 0
            memory_based = self.info.database in (None, '', ':memory:')
            if memory_based and no_pool:
                raise ValueError(
                    'SQLite in-memory database with an empty queue'
                    ' (pool_size = 0) is not possible due to data loss.'
                )
        return options

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup. In a web application or a multithreaded
        environment, never use a database without initialize it first,
        or connections will leak.
        """
        if not hasattr(app, 'databases'):
            app.databases = []
        if isinstance(app.databases, list):
            if self in app.databases:
                return
            app.databases.append(self)

        def shutdown(response=None):
            self.session.remove()
            return response

        def rollback(error=None):
            try:
                self.session.rollback()
            except Exception:
                pass

        self.set_flask_hooks(app, shutdown, rollback)
        self.set_bottle_hooks(app, shutdown, rollback)
        self.set_webpy_hooks(app, shutdown, rollback)

    def set_flask_hooks(self, app, shutdown, rollback):
        """Setup the ``app.after_request`` and ``app.on_exception``
        hooks to call ``db.session.remove()`` after each response, and
        ``db.session.rollback()`` if an error occurs.
        """
        if hasattr(app, 'after_request'):
            app.after_request(shutdown)
        if hasattr(app, 'on_exception'):
            app.on_exception(rollback)

    def set_bottle_hooks(self, app, shutdown, rollback):
        """Setup the bottle-specific ``after_request`` to call
        ``db.session.remove()`` after each response.
        """
        if hasattr(app, 'hook'):
            app.hook('after_request')(shutdown)

    def set_webpy_hooks(self, app, shutdown, rollback):
        """Setup the webpy-specific ``web.unloadhook`` to call
        ``db.session.remove()`` after each response.
        """
        try:
            import web
        except ImportError:
            return
        if not hasattr(web, 'application'):
            return
        if not isinstance(app, web.application):
            return
        app.processors.append(0, web.unloadhook(shutdown))

    @property
    def engine(self):
        """Gives access to the engine.
        """
        with self._engine_lock:
            connector = self.connector
            if connector is None:
                connector = EngineConnector(self)
                self.connector = connector
            return connector.get_engine()

    @property
    def metadata(self):
        """Proxy for ``Model.metadata``.
        """
        return self.Model.metadata

    @property
    def query(self):
        """Proxy for ``self.session.query``.
        """
        return self.session.query

    def add(self, *args, **kwargs):
        """Proxy for ``self.session.add``.
        """
        return self.session.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Proxy for ``self.session.delete``.
        """
        return self.session.delete(*args, **kwargs)

    def flush(self, *args, **kwargs):
        """Proxy for ``self.session.flush``.
        """
        return self.session.flush(*args, **kwargs)

    def commit(self):
        """Proxy for ``self.session.commit``.
        """
        return self.session.commit()

    def rollback(self):
        """Proxy for ``self.session.rollback``.
        """
        return self.session.rollback()

    def create_all(self):
        """Creates all tables.
        """
        self.Model.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drops all tables.
        """
        self.Model.metadata.drop_all(bind=self.engine)

    def reflect(self, meta=None):
        """Reflects tables from the database.
        """
        meta = meta or MetaData()
        meta.reflect(bind=self.engine)
        return meta

    def __repr__(self):
        return "<SQLAlchemy('{0}')>".format(self.uri)
