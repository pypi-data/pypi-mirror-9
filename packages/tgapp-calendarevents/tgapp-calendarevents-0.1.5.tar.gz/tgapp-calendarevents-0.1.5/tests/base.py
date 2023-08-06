from webtest import TestApp
import inspect
import transaction

from tg import AppConfig
from tg.configuration import milestones
from tg.configuration.auth import TGAuthMetadata
from tgext.pluggable import plug, app_model

from sqlalchemy import Integer, Column, Unicode
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from calendarevents import EventType


class FakeAppPackage(object):
    __file__ = __file__
    __name__ = 'tests'

    class lib(object):
        class helpers(object):
            pass
        helpers = helpers()

        class app_globals(object):
            class Globals():
                pass
        app_globals = app_globals()


class FakeSQLAModel(object):
    def __init__(self):
        self.DeclarativeBase = declarative_base()
        self.DBSession = scoped_session(sessionmaker(autoflush=True, autocommit=False,
                                                     extension=ZopeTransactionExtension()))

        class User(self.DeclarativeBase):
            __tablename__ = 'tg_user'

            user_id = Column(Integer, autoincrement=True, primary_key=True)
            user_name = Column(Unicode(16), unique=True, nullable=False)
            email_address = Column(Unicode(255), unique=True, nullable=False)
            display_name = Column(Unicode(255))

        self.User = User

    def init_model(self, engine):
        self.DBSession.configure(bind=engine)
        self.DeclarativeBase.metadata.drop_all(engine)
        self.DeclarativeBase.metadata.create_all(bind=engine)


class FakeUser(object):
    """
    Fake user that emulates an users without the need to actually
    query it from the database, it is able to trick sprox when
    resolving relations to the blog post Author.
    """
    def __int__(self):
        return 1

    def __getattr__(self, item):
        if item == 'user_id':
            return 1


class TestAuthMetadata(TGAuthMetadata):
    def authenticate(self, environ, identity):
        return 'user'

    def get_user(self, identity, userid):
        if userid:
            return FakeUser()

    def get_groups(self, identity, userid):
        if userid:
            return ['managers', 'calendarevents']
        return []

    def get_permissions(self, identity, userid):
        if userid:
            return ['calendarevents']
        return []


class FakeEventType(EventType):
    name = 'event_type'

    def get_linkable_entities(self, calendar):
        return []

    def get_linked_entity_info(self, event):
        return {'type': 'event_type', 'price': 20}


def configure_app():
    app_cfg = AppConfig(minimal=True)
    app_cfg.renderers = ['genshi']
    app_cfg.default_renderer = 'genshi'
    app_cfg.use_dotted_templatenames = True
    app_cfg.package = FakeAppPackage()
    app_cfg.use_toscawidgets2 = True
    app_cfg.sa_auth.authmetadata = TestAuthMetadata()
    app_cfg['beaker.session.secret'] = 'SECRET'
    app_cfg.auth_backend = 'sqlalchemy'

    app_cfg.package.model = FakeSQLAModel()
    app_cfg.use_sqlalchemy = True
    app_cfg['sqlalchemy.url'] = 'sqlite://'
    app_cfg.use_transaction_manager = True

    app_cfg.model = app_cfg.package.model
    app_cfg.DBSession = app_cfg.package.model.DBSession

    plug(app_cfg, 'calendarevents', event_types=[FakeEventType()], global_models=True, plug_bootstrap=False)

    # This is to reset @cached_properties so they get reconfigured for new backend

    return app_cfg


def create_app(app_config, auth=False):
    app = app_config.make_wsgi_app(skip_authentication=True)
    if auth:
        return TestApp(app, extra_environ=dict(REMOTE_USER='user'))
    else:
        return TestApp(app)


def flush_db_changes():
    app_model.DBSession.flush()
    transaction.commit()
