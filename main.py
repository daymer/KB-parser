from grab import Grab
import logging
from simple_salesforce import Salesforce
import pyodbc
import re
import traceback
from datetime import datetime
#configuring SQL connection:
server = 'ALISSON\SQLEXPRESS'
database = 'KnowledgeArticles'
username = 'KBparser'
password = '123@qwe'
driver = '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
#configuring SF connection:
sf = Salesforce(username='some', password='pass',
                security_token='here')
#configuring Grab:
logging.basicConfig(level=logging.INFO)
g = Grab()
g.setup(log_dir='log/KBpages')


def checking_existence(dictionary):
    cursor.execute(
        "select CONVERT(datetime,[Last_Modified],101) FROM [dbo].[KnowledgeArticles] where [url] = '" + dictionary[
            'URL'] + "'")
    row = cursor.fetchone()
    if row:
        try:
            slq_last_modified = re.findall('\(datetime\.datetime\((\d{4}),\s(\d*),\s(\d*),\s(\d*),\s(\d*)\),\s\)', str(row))
            slq_last_modified = datetime.strptime(str(str(slq_last_modified[0][0]) + '-' + str(slq_last_modified[0][1]) + '-' + str(slq_last_modified[0][2])), '%Y-%m-%d')
            return slq_last_modified
        except TypeError:
            print('Unable to parse slq_last_modified')
            return 'NONE'
    else:
        return 'NONE'

def get_fields_from_internet(dictionary):
    g.go(dictionary['URL'], follow_location=False)
    if g.doc.code == 301 or g.doc.code == 302:
        print(g.doc.url + ' doesn\'t exists')
        return 'not_exists'
    elif g.doc.code == 200:
        div = (g.doc.select('//div[@class="vrow"]/div[@class="col-12 border-bottom"]').text())
        try:
            dictionary['Products'] = re.findall('Products: (.*)\sVersion:', div)[0]
        except:
            dictionary['Products'] = 'NONE'
        try:
            dictionary['Version'] = re.findall('Version:\s(.*)\sPublished', div)[0]
        except:
            dictionary['Version'] = 'NONE'
        try:
            dictionary['Languages'] = re.findall('Languages:\s(.*)\sPrint', div)[0]
        except:
            dictionary['Languages'] = 'EN'
        return dictionary
    else:
        print('Error: unexpected answer code: ' + str(g.doc.code) + ' on page: ' + g.doc.url)
        return 'Error'


def get_fs_user_name_by_id(user_id):
    request = str(
        sf.query(
            "SELECT Name FROM user where Id='" + user_id + "'"))
    request_line = request.split("OrderedDict([('attributes', OrderedDict([('type', 'KnowledgeArticleVersion'), ")
    try:
        owner_name = re.findall("\('Name',\s'([A-Za-z'\s]*)'\)", str(request_line))
    except:
        owner_name = 'not defined'
    return owner_name[0]


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
                    'Id': str(result[0][0]),
                    'Title': str(result[0][1]),
                    'ArticleNumber': str(result[0][2]),
                    'OwnerId': str(result[0][3]),
                    'FirstPublishedDate': str(result[0][4]),
                    'LastPublishedDate': str(result[0][5]),
                    'KnowledgeArticleId': str(result[0][6]),
                    'URL': str('https://www.veeam.com/kb' + str(result[0][2])),
                    'OwnerName': get_fs_user_name_by_id(str(result[0][3]))
                }
                kb_last_modified = checking_existence(dict)
                if datetime.strptime(dict['LastPublishedDate'], '%Y-%m-%d') == kb_last_modified:
                    print(dict['URL'] + ' wasn\'t modified')
                    skipped += 1
                elif kb_last_modified == 'NONE':
                    dict_after_intrnet = get_fields_from_internet(dict)
                    if dict_after_intrnet != 'not_exists':
                        dict = dict_after_intrnet
                    else:
                        print(str(dict['URL']) + ' URL does\'t exists')
                        failed += 1
                        continue
                    try:
                        cursor.execute(
                            "insert into [dbo].[KnowledgeArticles] ([ID],[title],[url],[KB_ID],[Published],"
                            "[Last_Modified],[OwnerId],[KnowledgeArticleId],[Products],[Version],[Languages],"
                            "[Last_check],[is_uptodate],[OwnerName]) values (NEWID(),?,?,?,?,?,?,?,?,?,?,getdate(),'1',?)",
                            dict['Title'], dict['URL'], dict['Id'], dict['FirstPublishedDate'].replace('-', ''),
                            dict['LastPublishedDate'].replace('-', ''), dict['OwnerId'], dict['KnowledgeArticleId'],
                            dict['Products'], dict['Version'], dict['Languages'], dict['OwnerName'])
                        cnxn.commit()
                        print(str(dict['URL']) + ' was added to DB')
                        added += 1
                    except pyodbc.DataError:
                        cnxn.rollback()
                        error_handler = traceback.format_exc()
                        print(str(dict['URL'] + ' rolled back due to the following error:\n' + error_handler + '\n dict: ' + str(dict)))
                        failed += 1
                    except pyodbc.IntegrityError:
                        print(str(dict['URL']) + ' status: ')
                        print('...seems that this KB was already added')
                        skipped += 1
                        continue
                else:
                    #dict['LastPublishedDate'] != kb_last_modified
                    dict_after_intrnet = get_fields_from_internet(dict)
                    if dict_after_intrnet != 'not_exists':
                        dict = dict_after_intrnet
                    else:
                        failed += 1
                        print(str(dict['URL']) + ' URL does\'t exists')
                        continue
                    #here we will update DB... somehow
            except:
                error_handler = traceback.format_exc()
                print('....unable to parse FS KB entry:\n' + error_handler)
                failed += 1
                continue
    result = str(len(request_line)) + ' KBs were parsed, ' + str(added) + ' were added, ' + str(
        skipped) + ' were skipped and ' + str(failed) + ' were failed to become parsed or added'
    return result

print(fetch_new_kbs())




'''
cursor.execute("select @@VERSION")
row = cursor.fetchone()
if row:
    print(row)
'''