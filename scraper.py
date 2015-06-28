import urlparse
import requests
import os
import bs4
import json

# Names of the files that are saved by the scraper
dipjson4='diputados_4.json'
votejson4='votations_1282-4982.json'
dipjson5='diputados_5.json'
votejson5='votations_5004-10960.json'
dipjson6='diputados_6.json'
votejson6='votations_11108-19012.json'
dipjson8 = 'diputados_8.json'
votejson8 = 'votations_19192-20702.json'

# Base URL's for the scraping
urlLegActual = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getLegislaturaActual'
urlDip = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getDiputados_Periodo?prmPeriodoID='
urlPeriodosLeg = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getPeriodosLegislativos'
urlDipVig = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getDiputados_Vigentes'
urlVotings = 'http://opendata.congreso.cl/wscamaradiputados.asmx/getVotacion_Detalle?prmVotacionID='
party_keys=["IND","DC","PPD","PRSD","PS","RN","UDI","PRI","PC","IC"]

#Range of Voting ID numbers for each period
votID20022006 = [1282, 4982]
votID20062010 = [5004, 10960]
votID20102014 = [11108, 19012]
votID20142018 = [19192, 20702]


######### Code Taken from PA1 in CS122 - UNIVERSITY OF CHICAGO #########

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
    fails.
    '''

    try:
        return request.text.encode('utf-8') # We change the encoding
    except:
        print "read failed: " + request.url
        return ""

####### END OF COPIED CODE  ########

def read(url):
    '''
    Given a URL, it generates a request object, and then turns it into a
    String, which is turned into a Beautiful Soup XML object (not html), 
    with utf-8 encoding. 
    Returns the Beautiful Soup object
    ''' 
    req = get_request(url)
    xmlstring = read_request(req)
    xmlsoup = bs4.BeautifulSoup(xmlstring, 'xml', from_encoding="utf-8")   
    return xmlsoup


def read_diputados(diputados_soup, id_legislatura):
    '''
    Takes a Beautiful Soup XML object of the hole page, and scrapes and 
    finds all the Representatives of a given period of legislature.
    Legislature are named:
    4 -> 2002-2006
    5 -> 2006-2010
    6 -> 2010-2014
    8 -> 2014-2018 (current)
    Returns a dictionary with all the representatives for a given period
    '''
    diputados = {}
    dips_xml = diputados_soup.findAll('Diputado')
    for diputado in dips_xml:
        militancias = diputado.Militancias_Periodos.findAll('Militancia')
        for periodo in militancias:
            #print "I am in 2"
            if periodo.Periodo.ID.text==id_legislatura:
                #print 'I am in'
                agregar_diputado(diputados, diputado, periodo)
    return diputados


def agregar_diputado(diputados, diputado, periodo):
    '''
    It takes the dictionary created on read_diputados, a tag object with
    the representative's information and another tag object with the party
    Returns the updated dictionary.
    '''
    datos = [diputado.Nombre.get_text(), diputado.Apellido_Paterno.text, 
            diputado.Apellido_Materno.text, periodo.Periodo.Nombre.text, 
            periodo.Periodo.ID.text]
    registro = {int(diputado.DIPID.text): datos}
    partido = periodo.Partido['Codigo']
    if partido in diputados.keys():
        diputados[partido].update(registro)
    else:
        diputados[partido] = registro


def create_dipdict(num):
    '''
    Creates the Representatives dictionary by just specifing the 
    Legislatures ID number, calling the other functions.
    Returns the Dictionary.
    '''
    num = (str)(num)
    url = urlDip+num
    if num==8:
        url = urlDipVig
    xml_string = read(url)
    d = read_diputados(xml_string, num)
    return d


def create_dip_json(num):
    '''
    Creates a JSON file with the representatives information, by specifing
    the Legislatures ID.
    The file is encoded in utf-8. Acknowledgments to Gustav Larsson
    '''
    n = str(num)
    filename = 'diputados_'+n+'.json'
    dips = create_dipdict(num)
    open (filename, 'w').write(json.dumps(dips, ensure_ascii=False).encode('utf8'))


def read_votacion (votacion_soup, id_votacion):
    '''
    Given a tag object and a voting id, it returns a dictionary with
    the details of how every representative voting in it.
    '''
    voting = {}
    # This check if its and emty votation XML files. Without the checking
    # the program would crash
    if votacion_soup.ID:
        if int(votacion_soup.ID.text)!=id_votacion: #Double checking
            print "Error. Voting ID and XML Vote ID don't match"
            print id_votacion
        else:
            votos = votacion_soup.findAll('Voto')
            for diputado in votos:
                voting[int(diputado.DIPID.text)] = int(diputado.Opcion['Codigo'])
    return voting


def generate_voting_records(low, high):
    '''
    Given a higher and lower bound range of voting ID's, it scrapes all
    the XML web pages on the server for each ID in between, generating a
    dictionary with all the valid information.
    It outputs percentage of completion on the console, because it can take
    hours to run, depending on the speed of the web connection.
    '''
    voting_record = {}
    mult = 100.0/(high-low) #the multiplier
    for x in range(low, high+1): # must include upper bound
        num = (str)(x)
        url = urlVotings+num
        votacion_soup = read(url)
        record = read_votacion(votacion_soup, x)
        # If its not an empty dictionary. Many voting ID's in between
        # have no information.
        if record:  
            voting_record[x] = record
        completion = (x-low)*mult
        print "{0:.2f}".format(completion)+'%' #Just show 2 decimals
    return voting_record


def create_voting_json(low, high):
    '''
    Given the upper and lower bound, it creates a JSON file with the
    dictionary of generating_voting_records in it.
    '''
    n = str(low)+'-'+str(high)
    filename = 'votations_'+n+'.json'
    votations = generate_voting_records(low, high)
    with open (filename, 'w') as f:
        json.dump(votations, f)


def votings(id_legis):
    '''
    It calls create_voting_json with the correct upper and lower bounds
    by just specifing the Legislature ID
    '''
    n = str(id_legis)
    ids = {'4': votID20022006, '5': votID20062010,
            '6': votID20102014, '8': votID20142018}
    if n in ids.keys():
        create_voting_json(ids[n][0], ids[n][1])
    else:
        print "Error. Bad Period. 4, 5, 6 or 8 are valid"

def do():
    '''
    Runs the program, scrapes the web, creates the dictionaries
    and creates 8 json files.
    '''
    periods = [4,5,6,8]
    for x in periods:
        print 'Create the representatives json file for period '+str(x)+'...'
        create_dip_json(x)
        print 'DONE'
        print 'Create the votings json file for period '+str(x)+'...'
        votings(x)
        print 'DONE'
    print 'Program FINISHED'

if __name__ == "__main__":
    do()