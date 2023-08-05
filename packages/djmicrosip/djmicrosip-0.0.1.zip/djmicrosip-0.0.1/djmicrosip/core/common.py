#encoding:utf-8
from datetime import datetime
import os
import xlrd
from unidecode import unidecode
from django.db import connections

def exists_table_field(table_name, filed_name, using):
    c = connections[using].cursor()
    c.execute("SELECT 1 from RDB$RELATION_FIELDS rf where rf.RDB$RELATION_NAME = '%s' and rf.RDB$FIELD_NAME = '%s'"%(table_name, filed_name))
    registros = c.fetchall()
    c.close()
    exists = registros != []
    return exists

def split_seq(seq, n):
    """ para separar una lista en otra lista de listas en partes iguales.
    """
    lista = []
    for i in xrange(0, len(seq), n):
        lista.append(seq[i:i+n])
    return lista
    
def split_letranumero(folio):
    serie = ''
    for caracter in folio:
        if caracter.isalpha():
            serie= serie+ caracter
    if serie != '':
        serie_consecutivo = folio.split(serie)
    else:
        serie_consecutivo = '',int(folio)
    return serie, int(serie_consecutivo[1])

def get_object_or_empty(model, ):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model()


def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')
def get_claves_comercio_digital():

    book = xlrd.open_workbook(u'%s\\comercio_digital_claves.xlsx'%EXTRA_INFO['rura_datos_facturacion'])
    hoja = book.sheet_by_index(0)
    claves = {}
    for renglon in range(hoja.nrows):
        rfc = hoja.cell_value(renglon,0)
        clave = hoja.cell_value(renglon,1)
        if rfc != '':
            claves[rfc]= clave
    return claves

def get_certificado_digital(nombre_empresa):
    """ Para obtener certificados digitales. """
    carpeta_sellos = '%s\\sellos\\'%EXTRA_INFO['rura_datos_facturacion']
    carpeta_path   = '%s%s\\'%(carpeta_sellos,nombre_empresa)
    certificado, clave, password = None, None, None
    errors         = []

    try:
        archivos = os.listdir(carpeta_path)
    except WindowsError:
        errors.append('Carpeta no encontrada')
    else:
        for archivo in archivos:
            path =  "%s%s"%(carpeta_path, archivo)
            if archivo.endswith('.cer'):
                certificado = path
            if archivo.endswith('.key'):
                clave = path
            if archivo.endswith('.txt'):
                password = archivo.split('.txt')[0]
    
        if not certificado:
            errors.append('No se encontro archivo [.cer]')
        if not clave:
            errors.append('No se encontro archivo [.key]')
        if not password:
            errors.append('No se encontro archivo [contraseña]')

    return {
        'errors':errors,
        'certificado': certificado,
        'clave_privada': clave,
        'password': password,
    } 

def concatenar_conceptos(grupo_datos):
    encabezado = grupo_datos[0]
    valores = grupo_datos[1]

    datos = "[%s]\n"%encabezado

    for dato in valores:
        variable = dato[0]
        if not isinstance(dato[1], str) and not isinstance(dato[1], unicode):
            dato[1]= str(dato[1])
        valor = unidecode(dato[1])
        linea=  ("%s=%s\n"%(variable, valor))
        if (encabezado == 'Impuestos' ) and (dato[0] =='TotalImpuestosTrasladados' or dato[0]=='IEPSTasa'):
            linea = '%s\n'%linea

        datos = "%s%s"%(datos,linea)

    datos = u"%s\n"%datos 

    return datos

def certificar_factura(empresa_clave, using, clave_comercio_digital, **kwargs):
    'Funcion para certificar una factura'
    facturar_a = EXTRA_INFO['facturar_a']
    sistema_origen  = kwargs.get('sistema_origen', 0)
    documento_id  = kwargs.get('documento_id', 0)
    ruta_proyecto = os.path.dirname(os.path.realpath(__file__)).strip('\\comun').strip('api').strip('\\libs')
    ruta_comercio_digital_api = "%s\\libs\comercio_digital\\"%ruta_proyecto
    
    documento = VentasDocumento.objects.using(using).filter(pk=documento_id).values()[0]
    
    xml_data = []
    serie, folio = split_letranumero(documento['folio'])
    subtotal = documento['importe_neto'] - documento['otros_cargos'] - documento['impuestos_total'] - documento['retenciones_total']- documento['fpgc_total']

    #Comprobante
    xml_data.append([
        'Comprobante',[
            ['Version', '3.2'],
            ['TipoDeComprobante', 'ingreso'],
            ['Serie', serie],
            ['Folio', folio],
            ['Fecha', documento['fecha']],
            ['FormaDePago', 'Pago en una sola exhibición'],
            ['CondicionesDePago', 'Contado'],
            ['SubTotal', subtotal],
            # 'Descuento', descuento_importe],
            # 'MotivoDescuento', 'No aplica'],
            ['TipoCambio',  documento['tipo_cambio']],
            ['Moneda', 'MXN'],
            ['Total', documento['importe_neto']],
            ['MetodoDePago', 'No aplica'],
            ['LugarExpedicion',  'CUAUHTEMOC, CHIHUAHUA'],
            # ['NumCtaPago', 'No aplica'],
        ]
    ])
    
    #Emisor
    datos_empresa = Registry.objects.using(using).get(nombre='DatosEmpresa')
    datos_empresa = Registry.objects.using(using).filter(padre=datos_empresa)
    
    datos_emisor = {
        'Rfc': datos_empresa.get(nombre='Rfc').get_value().replace('-','').replace(' ',''),
        'Nombre': datos_empresa.get(nombre='Nombre').get_value(),
        'RegimenFiscal':datos_empresa.get(nombre='RegimenFiscal').get_value(),
        'Calle': datos_empresa.get(nombre='NombreCalle').get_value(),
        'NoExterior': datos_empresa.get(nombre='NumExterior').get_value(),
        'NoInterior': datos_empresa.get(nombre='NumInterior').get_value(),
        'Colonia': datos_empresa.get(nombre='Colonia').get_value(),
        # 'Localidad': datos_empresa.get(nombre='Nombre').get_value(),
        'Referencia': datos_empresa.get(nombre='Referencia').get_value(),
        'Municipio': datos_empresa.get(nombre='Ciudad').get_value(),
        'Estado': datos_empresa.get(nombre='Estado').get_value(),
        'Pais': datos_empresa.get(nombre='Pais').get_value(),
        'CodigoPostal': datos_empresa.get(nombre='CodigoPostal').get_value(),
    }
    
    xml_data.append([
        'Emisor',[  
            ['Rfc', datos_emisor['Rfc']],
            ['Nombre', datos_emisor['Nombre']],
            ['RegimenFiscal', datos_emisor['RegimenFiscal']],
            ['Calle', datos_emisor['Calle']],
            ['NoExterior', datos_emisor['NoExterior']],
            ['NoInterior', datos_emisor['NoInterior']],
            ['Colonia', datos_emisor['Colonia']],
            # ['Localidad', datos_emisor['Localidad']],
            ['Referencia', datos_emisor['Referencia']],
            ['Municipio', datos_emisor['Municipio']],
            ['Estado', datos_emisor['Estado']],
            ['Pais', datos_emisor['Pais']],
            ['CodigoPostal', datos_emisor['CodigoPostal']]
        ]
    ])
    # #EmisorExpedidoEn
    # xml_data.append([
    #     'EmisorExpedidoEn',[  
    #         ['Calle', 'hola'] ,
    #         ['NoExterior', 'hola'],
    #         ['NoInterior', 'hola'],
    #         ['Colonia', 'hola'],
    #         ['Localidad', 'hola'],
    #         ['Referencia', 'hola'],
    #         ['Municipio', 'hola'],
    #         ['Estado', 'hola'],
    #         ['Pais', 'hola'],
    #         ['CodigoPostal', 'hola'],
    #     ]
    # ])
    #requiremente  agragar unidecode
    #Receptor
    cliente = Cliente.objects.using(using).get(pk=documento['cliente_id'])
    direccion_cliente = ClienteDireccion.objects.using(using).filter(pk=documento['cliente_direccion_id']).values()[0]
    xml_data.append([
        'Receptor',[  
            ['Rfc', direccion_cliente['rfc_curp'].replace('-','').replace(' ','')],
            ['Nombre', cliente.nombre],
            ['Calle', direccion_cliente['calle_nombre']],
            ['NoExterior', direccion_cliente['numero_exterior']],
            ['NoInterior', direccion_cliente['numero_interior']],
            ['Colonia', direccion_cliente['colonia']],
            ['Localidad', direccion_cliente['poblacion']],
            ['Referencia', direccion_cliente['referencia']],
            ['Municipio', Ciudad.objects.using(using).get(pk=direccion_cliente['ciudad_id']).nombre],
            ['Estado',Estado.objects.using(using).get(pk=direccion_cliente['estado_id']).nombre],
            ['Pais', Pais.objects.using(using).get(pk=direccion_cliente['pais_id']).nombre ],
            ['CodigoPostal', direccion_cliente['codigo_postal']],
        ]
    ])

    #Conceptos
    xml_articulos_data = []
    detalles = VentasDocumentoDetalle.objects.using(using).filter(documento__id=documento['id']).values()
    contador = 0
    for detalle in detalles:
        contador = contador + 1
        articulo = Articulo.objects.using(using).get(pk=detalle['articulo_id'])
        xml_articulos_data.append([
            'Concepto%s'%contador,[  
                ['Cantidad', detalle['unidades']],
                ['Unidad', articulo.unidad_venta],
                ['NoIdentificacion', facturar_a['articulo_clave']],
                ['Descripcion', articulo.nombre],
                ['ValorUnitario', detalle['precio_unitario']],
                ['Importe', detalle['precio_total_neto']],
            ]
        ])

    xml_data.append(['list', xml_articulos_data])

    #Impuestos
    xml_data.append([
        'Impuestos',[  
            ['TotalImpuestosTrasladados', '0'],
            ['IEPSTrasladado', '0'],
            ['IEPSTasa', '0'],
            ['IVATrasladado', '0'],
            ['IVATasa', '0'],
        ]
    ])
    import codecs
    
    ruta_facturas = u"%s\\data\\facturas"%ruta_proyecto
    ruta_api = u"%s\\libs\\comercio_digital"%ruta_proyecto 
    ruta_archivo_ini = u"%s\\%s.ini"%(ruta_facturas, documento['folio'])

    archivo = codecs.open(ruta_archivo_ini, encoding='utf-8', mode='w+')

    for encabezado in xml_data:
        if encabezado[0] == 'list':
            for grupo_datos in encabezado[1]:
                archivo.write( concatenar_conceptos(grupo_datos) )    
        else:   
            archivo.write( concatenar_conceptos(encabezado) )         
            
    archivo.close()
    archivos_facturacion = get_certificado_digital(empresa_clave)
    #PROD para produccion
    #PRUEBAS PARA PRUEBAS
    if not archivos_facturacion['errors']:
        comando = '%s\\cd_sellar %s %s %s %s %s %s PRUEBAS SI'%(
                ruta_api,
                datos_emisor['Rfc'],
                clave_comercio_digital,
                ruta_archivo_ini, 
                archivos_facturacion['clave_privada'], 
                archivos_facturacion['certificado'], 
                archivos_facturacion['password']
            )
        os.system(comando)

        sat_file = codecs.open('%s.sat'%ruta_archivo_ini, encoding='utf-8')
        lineas = sat_file.readlines()
        sat_file.close()
        if lineas[0]==u'1\n':
            uuid = (lineas[1].replace('\n','').split('='))[1]
            xml_file = codecs.open('%s.xml'%ruta_archivo_ini, encoding='utf-8')
            xml = ''
            for linea in xml_file:
                xml = xml + linea
            xml_file.close()
            
            uso_folios_fiscales = ConfiguracionFolioFiscalUso.objects.using(using).get(documento= documento['id'])
            uso_folios_fiscales.xml = xml
            uso_folios_fiscales.prov_cert = 'CDIGITAL'
            uso_folios_fiscales.fechahora_timbrado = datetime.now().strftime("%Y-%m-%dT%I:%M:%S")
            uso_folios_fiscales.uuid = uuid
            uso_folios_fiscales.save(using=using,update_fields=['xml','prov_cert', 'fechahora_timbrado', 'uuid',])
            
            documento = VentasDocumento.objects.using(using).get(pk=documento_id)
            documento.cfd_certificado = 'S'
            documento.aplicado = 'S'
            documento.save(using=using, update_fields=['cfd_certificado','aplicado',]) 

            os.remove(ruta_archivo_ini)
            os.remove('%s.sat'%ruta_archivo_ini)
            os.remove('%s.xml'%ruta_archivo_ini)
        else:
            return False
    else:
        return False
    
    return True