import urllib, urllib2, json, cgi, webapp2

class SMSMasivo(dict):
    ''' Objeto para enviar sms. '''

    def __init__(self, apikey, pruebas=False):
        self.apikey = apikey
        self.pruebas= pruebas


    def send(self, mensaje, telefono, numregion=52):
        parametros_dic={'apikey':self.apikey,'mensaje': mensaje,'numcelular': telefono,'numregion':numregion}

        if self.pruebas:
            parametros_dic['sandbox']=1

        parametros = urllib.urlencode(parametros_dic)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept":"text/plain"}
        request_sms = urllib2.Request('http://www.smsmasivos.com.mx/sms/api.envio.new.php', parametros, headers)
        opener = urllib2.build_opener()
        respuesta = opener.open(request_sms).read()
        return json.loads(respuesta)

    def multisend(self, mensaje, telefono, numregion=52):
        parametros_dic={'apikey':self.apikey,'mensaje': mensaje,'numcelular': telefono,'numregion':numregion}

        if self.pruebas:
            parametros_dic['sandbox']=1

        parametros = urllib.urlencode(parametros_dic)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept":"text/plain"}
        request_sms = urllib2.Request('http://www.smsmasivos.com.mx/sms/api.multienvio.new.php', parametros, headers)
        opener = urllib2.build_opener()
        respuesta = opener.open(request_sms).read()
        return json.loads(respuesta)

    def credito(self):
        parametros = urllib.urlencode({'apikey':self.apikey})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept":"text/plain"}
        request_sms = urllib2.Request('http://www.smsmasivos.com.mx/sms/api.credito.new.php', parametros, headers)
        opener = urllib2.build_opener()
        respuesta = opener.open(request_sms).read()
        return json.loads(respuesta)