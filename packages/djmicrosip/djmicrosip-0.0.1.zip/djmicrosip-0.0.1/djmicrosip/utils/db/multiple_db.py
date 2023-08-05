import os
import fdb

class ConnectionDatabase(object):
    databases = []
    def __init__(self, host, path, user, password):
        self.path = path
        self.user = user
        self.password = password
        self.host = host
        self.databases = self._get_databases()

    def _get_databases(self):
        """
        Get connection databases
        """
        databases = []
        try:
            db= fdb.connect(host=self.host, user=self.user, password=self.password, database="%s\System\CONFIG.FDB"%self.path )
        except fdb.DatabaseError:
            pass
        else:
            cur = db.cursor()
            cur.execute("SELECT NOMBRE_CORTO FROM EMPRESAS")
            databases = cur.fetchall()
            db.close()

        return databases

class ConnectionDatabases(object):
    ''' 
    Objeto guardar las conexiones a las bases de datos. 
    '''
    
    connections = [] 
    
    def __init__(self):
        self.connections = self._load_connections()

    def _load_connections(self):
        """
        Return data bases connections added to configuration
        """

        connections = []
        host = "127.0.0.1"
        path = "C:\djmicrosip datos"
        user =  'SYSDBA' 
        password = '1'
        connection = ConnectionDatabase(host=host, path=path, user=user, password=password)
        connections.append(connection)
        
        return connections

    def get_connections_dic(self):
        """
        Return dictionary to add in DATABASES of django configuration.
        """

        connections = {}
        connection_id = 0
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        connections['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':  os.path.join(os.path.split(BASE_DIR)[0], 'data' ,'USERS.sqlite3'),
        }

        for connection in self.connections:
            connection_id +=1
            database_id = '%02d-CONFIG'%connection_id
            database_name = "%s//System//CONFIG.fdb"%connection.path
            connections[database_id] = {
                'ENGINE':'firebird',
                'NAME': database_name,
                'PORT': '3050',
                'OPTIONS': {'charset':'ISO8859_1'},
                'USER': connection.user,
                'PASSWORD': connection.password,
                'HOST': connection.host,
            }  

            for database in connection.databases:
                database_id = '%02d-%s'%(connection_id, database[0].replace(' ','_'))
                database_name = "%s/%s"%(connection.path,database[0])

                connections[database_id] = {
                    'ENGINE':'firebird',
                    'NAME': database_name,
                    'PORT': '3050',
                    'OPTIONS': {'charset':'ISO8859_1'},
                    'USER': connection.user,
                    'PASSWORD': connection.password,
                    'HOST': connection.host,
                } 

        return connections
