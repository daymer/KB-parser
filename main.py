from grab import Grab
import logging
from simple_salesforce import Salesforce
import pyodbc
import re
import traceback
from datetime import datetime
from PythonConfluenceAPI import ConfluenceAPI
import KB_upload
import Configuration
ConfluenceConfig = Configuration.ConfluenceConfig()
SQLConfig = Configuration.SQLConfig()
SFConfig = Configuration.SFConfig()
#configuring Confluence connection:
api = ConfluenceAPI(ConfluenceConfig.USER, ConfluenceConfig.PASS, ConfluenceConfig.ULR)
#configuring SQL connection:
cnxn = pyodbc.connect('DRIVER='+SQLConfig.Driver+';PORT=1433;SERVER='+SQLConfig.Server+';PORT=1443;DATABASE='+SQLConfig.Database+';UID='+SQLConfig.Username+';PWD='+SQLConfig.Password)
cursor = cnxn.cursor()
#configuring SF connection:
sf = Salesforce(username=SFConfig.User, password=SFConfig.Password, security_token=SFConfig.SecurityToken)
#configuring Grab:
g = Grab()
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
        #print(g.doc.url + ' doesn\'t exists')
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
    failed_urls = []
    updated = 0
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
                print(dict['URL'])
                kb_last_modified = checking_existence(dict)
                if datetime.strptime(dict['LastPublishedDate'], '%Y-%m-%d') == kb_last_modified:
                    #print(dict['URL'] + ' wasn\'t modified')
                    skipped += 1
                elif kb_last_modified == 'NONE':
                    dict_after_internet = get_fields_from_internet(dict)
                    if dict_after_internet != 'not_exists':
                        dict = dict_after_internet
                    else:
                        #print(str(dict['URL']) + ' URL does\'t exists')
                        failed += 1
                        failed_urls.append({dict['URL'], 'URL does not exists'})
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
                        #print(str(dict['URL'] + ' rolled back due to the following error:\n' + error_handler + '\n dict: ' + str(dict)))
                        failed += 1
                        failed_urls.append({dict['URL'], str('insert rolled back due to the following error:\n' + error_handler + '\n dict: ' + str(dict))})
                    except pyodbc.IntegrityError:
                        #print(str(dict['URL']) + ' already added')
                        skipped += 1
                        continue
                else:
                    #dict['LastPublishedDate'] != kb_last_modified
                    dict_after_internet = get_fields_from_internet(dict)
                    if dict_after_internet != 'not_exists':
                        dict = dict_after_internet
                    else:
                        # print(str(dict['URL']) + ' URL does\'t exists')
                        failed += 1
                        failed_urls.append({dict['URL'], 'URL does\'t exists'})
                        continue
                    #here we will update DB... somehow
                    try:
                        cursor.execute("UPDATE [dbo].[KnowledgeArticles] SET is_uptodate ='0' WHERE url = ?",
                                       dict['URL'])
                        cnxn.commit()
                        updated =+ 1
                        try:
                            cursor.execute(
                                "UPDATE [dbo].[KnowledgeArticles] SET [title]=?, [Last_Modified]=?,[Products]=?,[Version]=?, [Languages]=?, [Last_check]=GetDate(),[is_uptodate]='1' WHERE url = ?",
                                dict['Title'],dict['LastPublishedDate'],dict['Products'], dict['Version'], dict['Languages'],dict['URL'])
                            cnxn.commit()
                        except:
                            cnxn.rollback()
                            error_handler = traceback.format_exc()
                            print(str(dict[
                                          'URL'] + ' update was rolled back due to the following error:\n' + error_handler + '\n dict: ' + str(
                                dict)))
                            failed += 1
                    except:
                        cnxn.rollback()
                        error_handler = traceback.format_exc()
                        print(str(dict['URL'] + ' update was rolled back due to the following error:\n' + error_handler + '\n dict: ' + str(dict)))
                        failed += 1
            except:
                error_handler = traceback.format_exc()
                print('....unable to parse FS KB entry:\n' + error_handler)
                failed += 1
                continue
    result = {
        'parsed' : len(request_line),
        'added' : added,
        'skipped' : skipped,
        'failed' : failed,
        'updated' : updated
    }
    if result['failed'] == 0:
        return result
    else:
        return result,failed_urls

result = fetch_new_kbs()
if len(result) == 1:
    if result['added'] > 0 or result['updated'] > 0:
        print(result)
        Uploader = KB_upload.add_all_pages('17498235', 'List of all KBs', KB_upload.create_new_global_body(), '1081415')
        print(Uploader[0])
    else:
        print(result)
else:
    if result[0]['added'] > 0 or result[0]['updated'] > 0:
        print(result[0])
        print('Errors were found in: \n' + str(result[1]))
        Uploader = KB_upload.add_all_pages('17498235', 'List of all KBs', KB_upload.create_new_global_body(), '1081415')
        print(Uploader[0])
    else:
        print(result[0])
        print('Errors were found in: \n' + str(result[1]))


