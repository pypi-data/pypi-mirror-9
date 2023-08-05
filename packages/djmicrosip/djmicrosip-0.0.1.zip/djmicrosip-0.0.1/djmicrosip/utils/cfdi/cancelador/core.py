#encoding:utf-8
import os, codecs

from djmicrosip.utils.cfdi.core import CertificadoDigital, ClavesComercioDigital

class CanceladorSAT():
    ' Cancela faturas digitales en el SAT'

    def __init__(self, sellos_folder_path, rfc, **kwargs):
        self.errors = []
        self.sellos_folder_path = sellos_folder_path
        self.api_folder_path = "%s\\comercio_digital\\"%os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(self.sellos_folder_path):
            self.errors.append("No se encontro la carpeta %s"%self.sellos_folder_path)

        self.passwords = ClavesComercioDigital("%s\\comercio_digital_claves.xlsx"%self.sellos_folder_path)
        if self.passwords.errors:
            if not self.errors:
                 self.errors += self.passwords.errors

        self.rfc = rfc
        empresa_folder_name = kwargs.get('empresa_folder_name', self.rfc)
        self.certificado_digital = CertificadoDigital("%s\\sellos\\%s"%(self.sellos_folder_path, empresa_folder_name))
        
        self.cancelaciones_path = "%s\\cancelaciones\\%s\\"%(self.sellos_folder_path, empresa_folder_name)
        if os.path.exists(self.sellos_folder_path):
            if not os.path.exists(self.cancelaciones_path):
                os.mkdir(self.cancelaciones_path)
        
        try:
            self.password = self.passwords[rfc]
        except KeyError:
            if not self.errors:
                self.errors.append("No se encontro la contraseña en archivo [comercio_digital_claves.xlsx].")

    def is_valid(self):
        if not self.errors:     
            if not self.certificado_digital.is_valid():
                self.errors += self.certificado_digital.errors

        if not self.errors:
            return True

        return False

    def cancelar(self, folio_fiscal, **kwargs):
        if not self.errors:
            comando = '%s %s %s %s %s %s %s %s %s'%(
                "%scd_cancela.exe"%self.api_folder_path,
                self.rfc,
                self.password,
                self.rfc,
                folio_fiscal,
                self.certificado_digital.certificado_key, 
                self.certificado_digital.certificado_cer, 
                self.certificado_digital.password,
                self.cancelaciones_path
            )
            
            os.system(comando)

            sat_file_path = '%s\\CANC_%s.sat'%(self.cancelaciones_path, folio_fiscal)
            
            try:
                sat_file = codecs.open(sat_file_path, encoding='utf-8')
            except IOError:
                self.errors.append('Problema al generar archivo [.sat]')
            else:
                lineas = sat_file.readlines()
                
                sat_file.close()
                os.remove(sat_file_path)

                if lineas[0] != u'1\n' and lineas[0] != u'1':
                    self.errors.append(lineas[1])
        
        return self.errors