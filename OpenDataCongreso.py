__author__ = 'Santiago Larrain'
import urlparse
import requests
import os
import bs4
from xml.dom import minidom

urlLegActual = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getLegislaturaActual'
urlDip6 = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getDiputados_Periodo?prmPeriodoID=6'
urlPeriodosLeg = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getPeriodosLegislativos'
urlDipVig = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getDiputados_Vigentes'


######### CODIGO COPIADO DE CS122 - UNIVERSITY OF CHICAGO - PA1  #########

def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.
    Inputs:
        url: must be an absolute URL
    Outputs:
        request object or None
    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''
    try:
        html = requests.get(url)
        return html
    except:
        # fail on any kind of error
        return None
def read_request(request):
    '''
    Return data from request object.  Returns result or "" if the read
    fails..
    '''

    try:
        return request.text.encode('iso-8859-1')
    except:
        print "read failed: " + request.url
        return ""

def read(url):
    req = get_request(url)
    xmlstring = read_request(req)
    return xmlstring

def read_minidom (xml_string):
    xml = minidom.parseString(xmlstring)
    return xml

def read_bs4(xml_string, id_legislatura):
    xmlsoup = bs4.BeautifulSoup(xml_string, 'xml')
    diputados = {}
    dips_xml = xmlsoup.findAll('Diputado')
    for diputado in dips_xml:
        militancias = diputado.Militancias_Periodos.findAll('Militancia')
        for periodo in militancias:
            #print "I am in 2"
            if periodo.Periodo.ID.text==id_legislatura:
                #print 'I am in'
                agregar_diputado(diputados, diputado, periodo)
    return diputados

def agregar_diputado(diputados, diputado, periodo):
    datos = [diputado.Nombre.text, diputado.Apellido_Paterno.text, diputado.Apellido_Materno.text, periodo.Periodo.Nombre.text, periodo.Periodo.ID.text]
    registro = {int(diputado.DIPID.text): datos}
    partido = periodo.Partido['Codigo']
    if partido in diputados.keys():
        diputados[partido].update(registro)
    else:
        diputados[partido] = registro

def main():
    xmlstring = read(urlDip6)
    return read_bs4(xmlstring, '6')






