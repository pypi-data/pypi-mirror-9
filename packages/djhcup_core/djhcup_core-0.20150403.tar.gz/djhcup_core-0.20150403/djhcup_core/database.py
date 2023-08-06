from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import Table
from sqlalchemy.dialects import postgres
from django.conf import settings

conn_str = "postgresql+psycopg2://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s" % settings.DATABASES['djhcup']
engine = create_engine(conn_str)
meta = MetaData()
meta.bind = engine
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def check_table_exists(tbl_name):
	return engine.dialect.has_table(engine.connect(), tbl_name)

def get_table(tbl_name, schema=None):
	return Table(tbl_name.lower(), meta, schema=schema, autoload=True)

def compile_pg(stmt):
	return unicode(stmt.compile(dialect=postgres.dialect(), compile_kwargs={"literal_binds": True}))
