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
    cursor.execute("select [title],[url],[Products],[Version],[OwnerName],[Languages],[Published],[Last_Modified] "
                   "FROM [KnowledgeArticles].[dbo].[KnowledgeArticles] order by [url]")
    rows = cursor.fetchall()
    number_of_pages = 0
    for row in rows:
        if row:
            number_of_pages = number_of_pages + 1
            row[6] = str(row[6])[:10]
            row[7] = str(row[7])[:10]
            newbodysection = '<tr>' \
                             '<td> ' + str(number_of_pages) + '</td> ' \
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
        return str('pages were updated, numm of version: ' + str(number)), number
    except:
        return 'error', traceback.format_exc()

def create_new_global_body_by_product(product):
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
    cursor.execute(
        "select [title],[url],[Products],[Version],[OwnerName],[Languages],[Published],[Last_Modified] FROM [KnowledgeArticles].[dbo].[KnowledgeArticles] where Products = ? order by [url]", subject)
    rows = cursor.fetchall()
    number_of_pages = 0
    for row in rows:
        if row:
            newbodysection = new_body_gen(number_of_pages, row)
            globalbody = globalbody + newbodysection
    globalbody = globalbody + '</tbody></table>'
    return globalbody

def new_body_gen(number_of_pages, row):
    number_of_pages = number_of_pages + 1
    row[6] = str(row[6])[:10]
    row[7] = str(row[7])[:10]
    newbodysection = '<tr>' \
                     '<td> ' + str(number_of_pages) + '</td> ' \
                     '<td>' + row[0].replace('&', '&amp;').replace('<', '{').replace('>', '}') + '</td>' \
                     '<td><a href="' + row[1] + '">' + row[1] + '</a></td>' \
                     '<td>' + row[2].replace(';', ', ').replace('&', '&amp;') + '</td>' \
                     '<td>' + row[3] + '</td>' \
                     '<td>' + row[4].replace('inactive', ' ') + '</td>' \
                     '<td>' + row[5] + '</td>' \
                     '<td>' + row[6] + '</td>' \
                     '<td>' + row[7] + '</td>' \
                     '</tr>'
    return newbodysection

class ConfluenceSection:
    def create_start(self, product):
        layout_start ='<ac:layout-section ac:type="single">' \
                      '<ac:layout-cell>' \
                      '<h2>' + product + '</h2>' \
                      '<table>' \
                      '<tbody>' \
                      '<tr>' \
                      '<th> </th>' \
                      '<th>Title</th>' \
                      '<th>URL</th>' \
                      '<th>Product</th>' \
                      '<th>Version</th>' \
                      '<th>Author</th>' \
                      '<th>Translations</th>' \
                      '<th>Published</th>' \
                      '<th>LastModified</th>' \
                      '</tr>'
        return layout_start
    def create_ending(self, layout_start):
        layout_ending = '</tbody>' \
                          '</table>' \
                          '</ac:layout-cell>' \
                          '</ac:layout-section>'
        completed_layout = layout_start + layout_ending
        return completed_layout

layout = test.create_start(product)
layout = test.create_ending(layout)
print('<ac:layout>' + layout + '</ac:layout>')
