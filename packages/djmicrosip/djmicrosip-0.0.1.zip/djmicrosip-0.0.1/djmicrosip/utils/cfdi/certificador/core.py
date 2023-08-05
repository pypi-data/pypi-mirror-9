#encoding:utf-8
import os
import xlrd
import codecs

from djmicrosip.core.common import split_letranumero, concatenar_conceptos
from djmicrosip.utils.cfdi.core import CertificadoDigital, ClavesComercioDigital
from datetime import datetime

class CertificadorSAT():
    def __init__(self, sellos_folder_path,**kwargs):
        self.sellos_folder_path = sellos_folder_path
        self.api_folder_path = "%s\\comercio_digital\\"%os.path.dirname(os.path.realpath(__file__))
        self.modo = kwargs.get('modo', 'PRUEBAS')
        if self.modo != 'PROD':
            self.modo = 'PRUEBAS'
            
        self.passwords = ClavesComercioDigital("%s\\comercio_digital_claves.xlsx"%self.sellos_folder_path)
        self.errors = []

    def certificar(self, **kwargs):
        ini_file_path = kwargs.get('ini_file_path', "%sFT-001.ini"%self.api_folder_path )
        rfc = kwargs.get('rfc', 'AAA010101AAA')
        empresa_folder_name = kwargs.get('empresa_folder_name', rfc)
        
        try:
            password = self.passwords[rfc]
        except KeyError:
            if rfc == 'AAA010101AAA':
                password = 'PWD'
            else:
                password = None
                self.errors.append('no se encontro password')

        certificado_digital = CertificadoDigital("%s\\sellos\\%s"%(self.sellos_folder_path, empresa_folder_name))
        
        if certificado_digital.errors:
            self.errors += certificado_digital.errors

        if not certificado_digital.errors and password:
            comando = '%s %s %s %s %s %s %s %s NO'%(
                "%scd_sellar.exe"%self.api_folder_path,
                rfc,
                password,
                ini_file_path,
                certificado_digital.certificado_key, 
                certificado_digital.certificado_cer, 
                certificado_digital.password,
                self.modo
            )

        if not self.errors:
            os.system(comando)

        try:
            sat_file = codecs.open('%s.sat'%ini_file_path, encoding='utf-8')
        except IOError:
            self.errors.append('Problema al generar archivo [.sat]')
        else:
            lineas = sat_file.readlines()
            sat_file.close()

            if lineas[0] != u'1\n':
                try:
                    self.errors.append(lineas[1])
                except IndexError:
                    self.errors.append("Error en certificado probablemente esta vacio")
        return self.errors

def create_ini_file(documento_id, sellos_folder_path, facturar_a, using):
    'Funcion para certificar una factura.'
    from djmicrosip.ventas.ventas_documento.models import VentasDocumento, VentasDocumentoDetalle
    from djmicrosip.comun.clientes.models import Cliente, ClienteDireccion
    from djmicrosip.comun.direcciones.models import Ciudad, Estado, Pais
    from djmicrosip.comun.articulos.models import Articulo

    from djmicrosip_api.models_base.models import Registry

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
            ['FormaDePago', 'Pago en una sola exhibicion'],
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
        'RegimenFiscal':datos_empresa.get(nombre='RegimenFiscal').get_value() or '',
        'Calle': datos_empresa.get(nombre='NombreCalle').get_value() or '',
        'NoExterior': datos_empresa.get(nombre='NumExterior').get_value() or '',
        'NoInterior': datos_empresa.get(nombre='NumInterior').get_value() or '',
        'Colonia': datos_empresa.get(nombre='Colonia').get_value() or '',
        # 'Localidad': datos_empresa.get(nombre='Nombre').get_value(),
        'Referencia': datos_empresa.get(nombre='Referencia').get_value() or '',
        'Municipio': datos_empresa.get(nombre='Ciudad').get_value() or '',
        'Estado': datos_empresa.get(nombre='Estado').get_value() or '',
        'Pais': datos_empresa.get(nombre='Pais').get_value() or '',
        'CodigoPostal': datos_empresa.get(nombre='CodigoPostal').get_value() or '',
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
   
    #Receptor
    cliente = Cliente.objects.using(using).get(pk=documento['cliente_id'])
    direccion_cliente = ClienteDireccion.objects.using(using).filter(pk=documento['cliente_direccion_id']).values()[0]
    
    poblacion = ''
    if 'poblacion' in direccion_cliente:
        poblacion = direccion_cliente['poblacion']

    xml_data.append([
        'Receptor',[  
            ['Rfc', direccion_cliente['rfc_curp'].replace('-','').replace(' ','')],
            ['Nombre', cliente.nombre],
            ['Calle', direccion_cliente['calle_nombre']],
            ['NoExterior', direccion_cliente['numero_exterior']],
            ['NoInterior', direccion_cliente['numero_interior']],
            ['Colonia', direccion_cliente['colonia']],
            ['Localidad', poblacion],
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
    
    ruta_archivo_ini = u"%s\\facturas\\%s.ini"%(sellos_folder_path, documento['folio'])

    archivo = codecs.open(ruta_archivo_ini, encoding='utf-8', mode='w+')
    
    for encabezado in xml_data:
        if encabezado[0] == 'list':
            for grupo_datos in encabezado[1]:
                archivo.write( concatenar_conceptos(grupo_datos) )    
        else:   
            archivo.write( concatenar_conceptos(encabezado) )         
            
    archivo.close()

def save_xml_in_document(ruta_archivo_ini, using, documento_id):
    from djmicrosip.ventas.ventas_documento.models import VentasDocumento
    from djmicrosip_api.models_base.models import ConfiguracionFolioFiscalUso

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
        
        uso_folios_fiscales = ConfiguracionFolioFiscalUso.objects.using(using).get(documento= documento_id)
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