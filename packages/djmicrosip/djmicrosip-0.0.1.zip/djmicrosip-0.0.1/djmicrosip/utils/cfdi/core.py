#encoding:utf-8
import os
import xlrd

class ClavesComercioDigital(dict):
    ''' Objeto para guradar las claves de comercio digital. '''

    def __init__(self, path_file ):
        self.errors = []
        self.path_file =path_file
        self.load_passwords()

    def get_password(self, rfc):
        error = None
        book = xlrd.open_workbook(self.path_file)
        hoja = book.sheet_by_index(0)
        password = None
        for renglon in range(hoja.nrows):
            if hoja.cell_value(renglon,0) == rfc:
                password = hoja.cell_value(renglon,1)

        if not password:
            error ='No se encontro el password'

        return  password, error

    def load_passwords(self):
        try:
            book = xlrd.open_workbook(self.path_file)
        except IOError:
            self.errors.append('No se encontro el archivo %s'%self.path_file)
        else:
            hoja = book.sheet_by_index(0)
            for renglon in range(hoja.nrows):
                rfc = hoja.cell_value(renglon,0)
                clave = hoja.cell_value(renglon,1)
                if rfc != '':
                    self[rfc]= clave

class CertificadoDigital():
    """ Para obtener certificados digitales. """

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.certificado_cer = None
        self.certificado_key = None
        self.password = None
        self.errors = []
        self.load()

    def is_valid(self):
        if not self.errors:
            if not self.certificado_cer:
                self.errors.append("No se encontro archivo [.cer]")
            elif not self.certificado_key:
                self.errors.append("No se encontro archivo [.key]")
            elif not self.password:
                self.errors.append("No se encontro archivo [password]")

        if not self.errors:
            return True
            
        return False

    def load(self):
        try:
            archivos = os.listdir(self.folder_path)
        except WindowsError:
            self.errors.append("No se encontro carpeta de archivos")
        else:
            for archivo in archivos:
                file_path =  "%s\\%s"%(self.folder_path, archivo)
                if archivo.endswith('.cer'):
                    self.certificado_cer = file_path
                if archivo.endswith('.key'):
                    self.certificado_key = file_path
                if archivo.endswith('.txt'):
                    self.password = archivo.split('.txt')[0]