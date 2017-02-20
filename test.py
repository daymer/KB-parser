from simple_salesforce import Salesforce
import pyodbc
import re
server = 'sup-a1631\SQLEXPRESS'
database = 'KnowledgeArticles'
#database = 'VeeamBackup_02049319'
username = 'test'
password = '123@qwe'

driver= '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
sf = Salesforce(username='dmitriy.rozhdestvenskiy@veeam.com', password='I^C92!T!!27j',
                security_token='dNr44yHsFXaSuRmKXunWPlzS')
Request = str(
    sf.query(
        "SELECT ID, Title, ArticleNumber, OwnerID, FirstPublishedDate, LastPublishedDate, KnowledgeArticleID  FROM KnowledgeArticleVersion where PublishStatus='Online' and language ='en_US'"))
ReResult = re.findall("\('Id',\s'(ka\d{10}\w{6})'\),\s\('Title',\s'([0-9a-zA-Z_\s]*)'\),\s\('ArticleNumber',\s'00000(\d{4})'\),\s\('OwnerId',\s'(\d{10}\w{8})'\),\s\('FirstPublishedDate',\s'(201\d-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.\d{3}\+\d{4}'\),\s\('LastPublishedDate',\s'(201\d-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}.\d{3}\+\d{4}'\),\s\('KnowledgeArticleId',\s'(kA\d{10}\w{6})'\)\]\),", Request)
counter = 0
for Result in ReResult:
    Dict = {
    'Id ' : str(Result[0]),
    'Title ' : str(Result[1]),
    'ArticleNumber ' : str(Result[2]),
    'OwnerId ' : str(Result[3]),
    'FirstPublishedDate ' : str(Result[4]),
    'LastPublishedDate ' : str(Result[5]),
    'KnowledgeArticleId ' : str(Result[6])
    }
    print(Dict)
    counter = counter + 1

print(counter)
cursor.execute("select @@VERSION")
row = cursor.fetchone()
if row:
    print(row)