from grab import Grab
import logging
from simple_salesforce import Salesforce
import pyodbc
import re
import traceback
#configuring SQL connection:
server = 'ALISSON\SQLEXPRESS'
database = 'KnowledgeArticles'
username = 'KBparser'
password = '123@qwe'
driver = '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
#configuring SF connection:
sf = Salesforce(username='dmitriy.rozhdestvenskiy@veeam.com', password='I^C92!T!!27j',
                security_token='dNr44yHsFXaSuRmKXunWPlzS')
#configuring Grab:
logging.basicConfig(level=logging.INFO)
#g = Grab()
#g.setup(log_dir='log/grab')


def fetch_new_kbs():
    skipped = 0
    added = 0
    failed = 0
    request = str(
        sf.query(
            "SELECT ID, Title, ArticleNumber, OwnerID, FirstPublishedDate, LastPublishedDate, KnowledgeArticleID  FROM KnowledgeArticleVersion where PublishStatus='Online' and language ='en_US'"))
    request_line = request.split("OrderedDict([('attributes', OrderedDict([('type', 'KnowledgeArticleVersion'), ")
    total = re.findall("OrderedDict\(\[\('totalSize',\s(\w*)\)", request_line[0])
    del request_line[0]
    if len(request_line) < int(total[0]):
        print('not all KB were parsed: ' + str(len(request_line)) + '<' + str(total[0]))
    else:
        for Line in request_line:
            try:
                result = re.findall(
                    "\('Id',\s'(ka\d*\w*)'\),\s\('Title',\s['\"](.*)['\"]\),\s\('ArticleNumber',\s'00000(\d{4})'\),\s\('OwnerId',\s'(\d{10}\w{8})'\),\s\('FirstPublishedDate',\s'(201\d-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.\d{3}\+\d{4}'\),\s\('LastPublishedDate',\s'(201\d-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.\d{3}\+\d{4}'\),\s\('KnowledgeArticleId',\s'(kA\w*)'\)\]\)",
                    Line)
                dict = {
                'Id' : str(result[0][0]),
                'Title' : str(result[0][1]),
                'ArticleNumber' : str(result[0][2]),
                'OwnerId' : str(result[0][3]),
                'FirstPublishedDate' : str(result[0][4]),
                'LastPublishedDate' : str(result[0][5]),
                'KnowledgeArticleId' : str(result[0][6]),
                'URL' : str('https://www.veeam.com/kb' + str(result[0][2]))
                }
            except:
                error_handler = traceback.format_exc()
                print('....unable to parse KB entry:\n' + error_handler)
                failed += 1
                continue
            #print(str(dict['URL']) + ' status: ')
            try:
                cursor.execute("insert into [dbo].[KnowledgeArticles] ([ID],[title],[url],[KB_ID],[Published],[Last_Modified],[OwnerId],[KnowledgeArticleId]) values (NEWID(),?,?,?,?,?,?,?)", dict['Title'], dict['URL'], dict['Id'], dict['FirstPublishedDate'].replace('-', ''), dict['LastPublishedDate'].replace('-', ''), dict['OwnerId'], dict['KnowledgeArticleId'])
                cnxn.commit()
                print(str(dict['URL']) + ' status: ')
                print('....committed')
                added += 1
            except pyodbc.DataError:
                cnxn.rollback()
                error_handler = traceback.format_exc()
                print(str(dict['URL']) + ' status: ')
                print('....rolled back due to the following error:\n' + error_handler + '\n dict: ' + str(dict))
                failed += 1
            except pyodbc.IntegrityError:
                #print(str(dict['URL']) + ' status: ')
                #print('...seems that this KB was already added')
                skipped += 1
                continue
    result = str(len(request_line)) + ' KBs were parsed, ' + str(added) + ' were added, ' + str(skipped) + ' were skipped and ' + str(failed) + ' were failed to become parsed or added'
    return result
Result = fetch_new_kbs()
print(Result)

#g.go(path, follow_location = False)



'''
cursor.execute("select @@VERSION")
row = cursor.fetchone()
if row:
    print(row)
'''