import psycopg2
import psycopg2.extras
import psycopg2.extensions
import logging

class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.warning(self.mogrify(sql, args))
        psycopg2.extensions.cursor.execute(self, sql, args)

class Postgres:
    def __init__(self, link):
        self.link = link

    def get_cursor(self):
        cur = self.link.cursor(cursor_factory=LoggingCursor)
        return cur

    def get_real_dict_cursor(self):
        cur = self.link.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return cur

    def execute(self, query, *params, **kparams):
        if len(params) == 0:
            params = kparams
        cur = self.get_cursor()
        cur.execute(query, params)
        return cur
    
    def safe_execute(self, query, *params, **kparams):
        if len(params) == 0:
            params = kparams
        cur = self.get_cursor()
        try:
            cur.execute(query, params)
        except psycopg2.ProgrammingError:
            pass
        return cur

    def insert(self, query, *params, **kparams):
        if len(params) == 0:
            params = kparams
        self.execute(query, *params)
        return self.query("SELECT lastval()", [])[0][0]
    
    def query(self, query, *params, **kparams):
        if len(params) == 0:
            params = kparams
        cur = self.get_cursor()
        cur.execute(query, params)
        return stringify(cur.fetchall())
    
    def meta_query(self, query, *params, **kparams):
        cur = self.get_cursor()
        cur.execute(query, params)
        return stringify(cur.fetchall()), [desc[0] for desc in cur.description]

    def commit(self):
        if self.link != None:
            self.link.commit()

    def close(self):
        if self.link != None:
            self.link.close()

def stringify(data):
    return [[str(column) for column in row] for row in data]

class PostgresGateway:
    def __init__(self, server, port, user, password, dbname):
        self.link = Postgres(psycopg2.connect(host=server, port=port, user=user, password=password, dbname=dbname))

    def getschema(self, params):
        database_names = []
        result = self.link.query('SELECT datname FROM pg_database WHERE datistemplate = false')
        for row in result:
            database_names.append(row[0])
        return database_names

    def get_fields_for_table(self, schema, table_name):
        fields = []
        result = self.link.query('SELECT * FROM information_schema.columns WHERE table_catalog = %s AND table_name   = %s', schema, table_name)
        for row in result:
            fields.append({'name':row[3], 'type':row[7]})
        return fields

    def gettables(self, params):
        result = self.link.query('SELECT table_name FROM information_schema.tables WHERE table_type = %s  AND table_schema NOT IN (%s, %s)', 'BASE TABLE', 'pg_catalog', 'information_schema')
        table_names = []
        for row in result:
            table_names.append({'name':row[0], 'fields': self.get_fields_for_table(params['db'], row[0])})
        return table_names

    def formatSql(self, params):
        import sqlparse
        return {'formatted': sqlparse.format(params['query'], reindent=True)}

    def execute(self, params):
        result, columns = self.link.meta_query(params['query'])
        r = {'columns': columns, 'data': result, 'message':'{} Rows returned'.format(len(result))}
        return r

    def explain(self, params):
        result, columns = self.link.meta_query('EXPLAIN ' + params['query'])
        r = {'columns': columns, 'data': result, 'message':'{} Rows returned'.format(len(result))}
        return r

    def loaddata(self, params):
        params = {'query':'select * from "{}"'.format(params['table'])}
        return self.execute(params)

