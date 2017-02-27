from PythonConfluenceAPI import ConfluenceAPI
import pyodbc
import traceback

api = ConfluenceAPI('user', 'password', 'http://ee.support2.veeam.local')
#configuring SQL connection:
server = 'sup-a1631\SQLEXPRESS'
database = 'KnowledgeArticles'
username = 'test'
password = 'password'
driver = '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
def create_new_global_body():
    globalbody = '<table>' \
                 '<tbody>' \
                 '<tr>' \
                 '<th> </th>' \
                 '<th>Title</th>' \
                 '<th>URL</th>' \
                 '<th>Product</th>' \
                 '<th>Version</th>' \
                 '<th>Author</th>' \
                 '<th>Translations</th>' \
                 '<th>Published</th>' \
                 '<th>LastModified</th>' \
                 '</tr>'
    cursor.execute("select [title],[url],[Products],[Version],[OwnerName],[Languages],[Published],[Last_Modified] FROM [KnowledgeArticles].[dbo].[KnowledgeArticles] order by [url]")
    rows = cursor.fetchall()
    number = 0
    for row in rows:
        if row:
            number = number + 1
            row[6] = str(row[6])[:10]
            row[7] = str(row[7])[:10]
            newbodysection = '<tr>' \
                             '<td> ' + str(number) + '</td> ' \
                             '<td>' + row[0].replace('&', '&amp;').replace('<', '{').replace('>', '}') + '</td>' \
                             '<td><a href="' + row[1] + '">' + row[1] + '</a></td>' \
                             '<td>' + row[2].replace(';', ', ').replace('&', '&amp;') + '</td>' \
                             '<td>' + row[3] + '</td>' \
                             '<td>' + row[4].replace('inactive', ' ') + '</td>' \
                             '<td>' + row[5] + '</td>' \
                             '<td>' + row[6] + '</td>' \
                             '<td>' + row[7] + '</td>' \
                             '</tr>'
            globalbody = globalbody + newbodysection
    globalbody = globalbody + '</tbody></table>'
    return globalbody
def add_all_pages(content_id, title, pagebody, ancestor):
    history = api.get_content_history_by_id(content_id,expand='history.lastUpdated')
    number = history['lastUpdated']['number']
    content ={
        "id" : content_id,
        "type": "page",
        "title": title,
        "ancestors": [{"type": "page", "id": ancestor}], #http://ee.support2.veeam.local/pages/viewpage.action?pageId=1081415
        "space": {
            "key": "VB"
        },
        "version": {
            "number": number+1,
            "minorEdit": 'false'
        },
        "body": {
            "storage": {
                "value": pagebody,
                "representation": "storage"
            }
        }
    }
    try:
        api.update_content_by_id(content, content_id)
        return str(str(number) + ' pages were updated'), number
    except:
        return 'error', traceback.format_exc()

ContentID = '17498235'
Title = 'List of all KBs'
print(add_all_pages(ContentID, Title, create_new_global_body(), '1081415'))