from grab import Grab
import logging
import re
from simple_salesforce import Salesforce
logging.basicConfig(level=logging.INFO)
g = Grab()
g.setup(log_dir='log/grab')
sf = Salesforce(username='dmitriy.rozhdestvenskiy@veeam.com', password='I^C92!T!!27j',
                security_token='dNr44yHsFXaSuRmKXunWPlzS')

for ID in range(2162, 2163):
    KBnumm = str(ID)
    path = 'https://www.veeam.com/kb' + KBnumm
    g.go(path, follow_location = False)
    if g.doc.code == 301 or g.doc.code == 302:
        print(g.doc.url + ' doesn\'t exists')
    elif g.doc.code == 200:
        DIV = (g.doc.select('//div[@class="vrow"]/div[@class="col-12 border-bottom"]').text())
        Request = str(
            sf.query(
                "SELECT id FROM Articles__c where ArticleTitle ='Failed load library during application aware processing of oracle running on Linux'"))
                #"SELECT id FROM Solution where SolutionName ='00000" + str(ID) + "'"))
        print(Request)
        Dict = {
            'title' : g.doc.select('//title').text(),
            'url' : g.doc.url,
            'KB ID' : re.findall('KB ID: ([0-9]*)', DIV)[0],
            'Products': re.findall('Products: (.*)\sVersion:', DIV)[0],
            'Version': re.findall('Version:\s(.*)\sPublished', DIV)[0],
            'Published': re.findall('Published:\s(20\d{2}-\d{2}-\d{2})', DIV)[0],
            'Last Modified': re.findall('Modified:\s(20\d{2}-\d{2}-\d{2})', DIV)[0]
            #'Languages': re.findall('Modified:\s(20\d{2}-\d{2}-\d{2})', DIV)[0]
        }

        print(Dict['title'])
        print(Dict)
    else:
        print('Error: unexpected answer code: ' + str(g.doc.code) + ' on page: ' + g.doc.url)
