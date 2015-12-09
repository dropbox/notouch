import rethinkdb as r
import tornado.gen

TABLES = ["dhcpack", "dhcpserverstats", "hosts"]

def create_database(host, port, db):
	"""
	Utility function to create the rethinkdb database and tables for notouch.
	"""
	conn = r.connect(host=host, port=port, db=db)

	if db not in r.db_list().run(conn):
		r.db_create(db).run(conn)
	discovered_tables = r.db(db).table_list().run(conn)
	for table in TABLES:
		if table not in discovered_tables:
			r.db(db).table_create(table).run(conn)

	return conn
	# TODO: Create indexes here.


def drop_database(rethinkdb_conn, db, testing=False):
	"""
	Utility function to drop the rethinkdb database and tables for notouch.

	rethinkdb_conn - A rethinkdb connection object.
	testing - Drop the database without prompting.
	"""
	if db in r.db_list().run(rethinkdb_conn) and testing:
		r.db_drop(db)

	# TODO: Implement drop with prompting for non-test mode.


def clean_database(rethinkdb_conn, db, testing=False):
	"""
	Utility function to drop the rethinkdb database and tables for notouch.

	rethinkdb_conn - A rethinkdb connection object.
	testing - Drop the database without prompting.
	"""
	if db not in r.db_list().run(rethinkdb_conn):
		return
	for table in TABLES:
		r.db(db).table(table).delete().run(rethinkdb_conn)

	# TODO: Implement drop with prompting for non-test mode.