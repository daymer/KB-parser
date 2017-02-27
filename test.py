from simple_salesforce import Salesforce
import re
sf = Salesforce(username='dmitriy.rozhdestvenskiy@veeam.com', password='I^C92!T!!27j',
                security_token='dNr44yHsFXaSuRmKXunWPlzS')

def get_fs_user_name_by_id:
    request = str(
        sf.query(
            "SELECT Name FROM user where Id='00560000001YxOLAA0'"))
    request_line = request.split("OrderedDict([('attributes', OrderedDict([('type', 'KnowledgeArticleVersion'), ")
    OwnerName = re.findall("\('Name',\s'([A-Za-z'\s]*)'\)", str(request_line))
    print(OwnerName[0])
