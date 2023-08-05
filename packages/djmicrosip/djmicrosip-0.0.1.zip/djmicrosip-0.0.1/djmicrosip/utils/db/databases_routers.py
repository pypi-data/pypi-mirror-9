djmicrosip_APS = (
    'general',
    'listas',
    'impuestos',
    'direcciones',
    'clientes',
    'articulos',
    'Inventarios',
    'inventarios_catalogos',
    'inventarios_documentos',
    'inventarios_otros',
    'Ventas',
    'ventas_documentos',
    'ventas',
    'punto_de_venta_listas',
    'punto_de_venta_documentos',
    'Contabilidad', 
    'contabilidad_catalogos',
    'contabilidad_listas',
    'contabilidad_documentos',
)

    

class MainRouter(object):
    """
    A router to control all database operations on models.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'system':
            from djmicrosip.core.middleware import my_local_global
            return '%02d-CONFIG'% my_local_global.conexion_activa
        elif model._meta.app_label == 'auth':
            return 'default'
        elif model._meta.app_label == 'django':
            return 'default'
        elif model._meta.app_label == 'djmicrosip_admin':
            return 'default'
        elif  model._meta.app_label in djmicrosip_APS:

            from djmicrosip.core.middleware import my_local_global
            if my_local_global.conexion_activa != None  and my_local_global.database_name != None:
                return '%02d-%s'% (my_local_global.conexion_activa ,my_local_global.database_name)

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        
        if model._meta.app_label == 'system':
            from djmicrosip.core.middleware import my_local_global
            return '%02d-CONFIG'% my_local_global.conexion_activa
        elif model._meta.app_label == 'auth':
            return 'default'
        elif model._meta.app_label == 'django':
            return 'default'
        elif model._meta.app_label == 'djmicrosip_admin':
            return 'default'
        elif model._meta.app_label in model._meta.app_label in djmicrosip_APS:
            from djmicrosip.core.middleware import my_local_global
           
            if my_local_global.conexion_activa != None  and my_local_global.database_name != None:
                return '%02d-%s'% (my_local_global.conexion_activa ,my_local_global.database_name)

        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label  == obj2._meta.app_label:
           return True
        if ((obj1._meta.app_label  == 'auth' and obj2._meta.app_label == 'django') or 
            (obj1._meta.app_label  == 'auth' and obj2._meta.app_label == 'djmicrosip_admin') or 
            (obj1._meta.app_label  == 'django' and obj2._meta.app_label == 'auth') or 
            (obj1._meta.app_label  == 'django' and obj2._meta.app_label == 'djmicrosip_admin') or 
            (obj1._meta.app_label  == 'djmicrosip_admin' and obj2._meta.app_label == 'auth') or
            (obj1._meta.app_label  == 'djmicrosip_admin' and obj2._meta.app_label == 'django')):
           return True           
        
        elif ( obj1._meta.app_label  in djmicrosip_APS and obj2._meta.app_label in djmicrosip_APS):
            return True

        return False

    def allow_syncdb(self, db, model):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        
        if model._meta.app_label == 'system' or 'CONFIG' in db:
            return False
        elif model._meta.app_label == 'auth' and db != 'default':
            return False
        elif model._meta.app_label == 'django' and db != 'default':
            return False
        elif db == 'default' and model._meta.app_label in djmicrosip_APS:
            return False
        else:
            return True

        return None