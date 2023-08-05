=====
Django djmicrosip core
=====

djmicrosip_VERSION = 2014

=====
load apps
=====

'django_dynamic_models',
# MODULOS djmicrosip
# Otros
'djmicrosip.comun.general',
'djmicrosip.comun.listas',
'djmicrosip.comun.impuestos',
'djmicrosip.comun.direcciones',
'djmicrosip.comun.clientes',
'djmicrosip.comun.articulos',
# Inventarios
'djmicrosip.inventarios.inventarios_catalogos',
'djmicrosip.inventarios.inventarios_documentos',
'djmicrosip.inventarios.inventarios_otros',
# Ventas
'djmicrosip.ventas.ventas_documentos',
# Punto de ventas
'djmicrosip.punto_de_venta.punto_de_venta_listas',
'djmicrosip.punto_de_venta.punto_de_venta_documentos',
# Contabilidad 
'djmicrosip.contabilidad.contabilidad_catalogos',
'djmicrosip.contabilidad.contabilidad_listas',
'djmicrosip.contabilidad.contabilidad_documentos',
'ejemplo',

=====
load djmicrosip databases
=====

'''
DATABASE_ROUTERS = ['djmicrosip.utils.db.databases_routers.MainRouter']
from djmicrosip.utils.db.multiple_db import ConnectionDatabases as djmicrosip_databases
DATABASES = djmicrosip_databases().get_connections_dic()

'''