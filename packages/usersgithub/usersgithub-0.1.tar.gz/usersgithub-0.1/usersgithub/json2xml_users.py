import requests
import xmltodict

users = input('Informe o usuario do Github: ')

json_user = requests.get('https://api.github.com/users/%s' %users)

dict_user = {}
dict_user['!-- Dados do usuario %s obtidos pela API do Github --' %users] = json_user.json()

xml_user = xmltodict.unparse(dict_user)

f = open('xml_usersgithub.xml', 'w')
f.writelines(xml_user)
f.close
