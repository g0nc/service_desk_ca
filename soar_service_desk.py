import requests
import datetime
import re
import json
import xmltodict
import os
import argparse
import sys
import time
import xml.etree.ElementTree as ET
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def parsing_to_json(xml):

        data = ET.fromstring(xml)[0][0][0].text

        data = xmltodict.parse(data)

        return(json.dumps(data))


def request_ca(operation_name, body_xml):
        url = "https://caserver:8443/axis/services/USD_R11_WebService?wsdl"

        # Define o cabeçalho da requisição SOAP
        headers = {
                "Content-Type": "text/xml;charset=UTF-8",
                "SOAPAction": f"{url}#{operation_name}"
        }

        # Define o corpo da requisição SOAP
        body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://www.ca.com/UnicenterServicePlus/ServiceDesk">
                <soapenv:Header/>
                <soapenv:Body>
                        <ser:{operation_name}>
                                {body_xml}
                        </ser:{operation_name}>
                </soapenv:Body>
        </soapenv:Envelope>"""

        response = requests.post(url, headers=headers, data=body, verify=False)

        return response.content.decode("utf-8")



def login():
        operation_name = "loginService"

        p = """password"""
        body_xml = f"""
        <username>user</username>
        <password>{p}</password>
        <policy>BFU_POLICY</policy>"""

        response = request_ca(operation_name, body_xml)


        root = ET.fromstring(response)

        sid = root[0][0][0].text

        with open("sid.txt", "w") as f:
                f.write(sid)

        return sid


def logout(sid):
        operation_name = "logout"

        body_xml = f"""
        <sid>{sid}</sid>
        """

        response = request_ca(operation_name, body_xml)

        return response



def get_ticket(sid, ref_num):
        operation_name = "doSelect"

        body_xml = f"""
        <sid>{sid}</sid>
        <objectType>cr</objectType>
        <whereClause>ref_num like '%{ref_num[0]}%'</whereClause>
        <maxRows>1</maxRows>
        <attributes>
        <!--1ormorerepetitions:-->
        <string>id</string>
        <string>z_srl_GrupoOriginador</string>
        <string>group</string>
        <string>category</string>
        <string>summary</string>
        <string>description</string>
        </attributes>
        """

        response = request_ca(operation_name, body_xml)

        formated = json.loads(parsing_to_json(response))

        #return formated['UDSObjectList']['UDSObject']['Attributes']['Attribute']
        return response


def get_affected_resource(sid, resource):
        operation_name = "doSelect"
        resource = str(resource)
        resource = resource.replace("['", "")
        resource = resource.replace("']", "")

        body_xml = f"""
        <sid>{sid}</sid>
        <objectType>nr</objectType>
        <whereClause>name LIKE '%{resource}%' and delete_flag = 0</whereClause>
        <maxRows>100</maxRows>
        <attributes>
        <!--1ormorerepetitions:-->
        
        </attributes>
        """

        response = request_ca(operation_name, body_xml)
        #print(response)

        #formated = json.loads(parsing_to_json(response))

        #id_resource = formated['UDSObjectList']['UDSObject']['Attributes']['Attribute'][0]['AttrValue']
        #solution_group = formated['UDSObjectList']['UDSObject']['Attributes']['Attribute'][1]['AttrValue']
        
        try:
        
          parser = re.search(r"nr:(.*?)&lt", str(response))
          affected_resource = parser.group(1)
        
        except:
          print("exception encontrado")

        return affected_resource



def do_select(sid, object_type, where_clause, max_rows):
        operation_name = "doSelect"

        body_xml = f"""
        <sid>{sid}</sid>
        <objectType>{object_type}</objectType>
        <whereClause>{where_clause}</whereClause>
        <maxRows>{max_rows}</maxRows>
        <attributes>
        <!--1ormorerepetitions:-->
        <string>id</string>
        </attributes>
        """

        response = request_ca(operation_name, body_xml)

        return response


def get_user_id(sid, user):
        operation_name = "doSelect"

        body_xml = f"""
        <sid>{sid}</sid>
        <objectType>cnt</objectType>
        <whereClause>userid='{user}'</whereClause>
        <maxRows>1</maxRows>
        <attributes>
        <!--1ormorerepetitions:-->
        <string>id</string>
        <string>z_srl_GrupoOriginador</string>
        </attributes>
        """

        response = request_ca(operation_name, body_xml)

        formated = json.loads(parsing_to_json(response))

        id_user = formated['UDSObjectList']['UDSObject']['Attributes']['Attribute'][0]['AttrValue']
        origin_group = formated['UDSObjectList']['UDSObject']['Attributes']['Attribute'][1]['AttrValue']

        return id_user, origin_group
        

def get_group(sid, group):

       operation_name = "doSelect"

       
       #print(str(group))
       body_xml = f"""
       <sid>{sid}</sid>
       <objectType>grp</objectType>
       <whereClause>alias LIKE '%{group}%'</whereClause>
       <maxRows>-1</maxRows>
       <attributes>
       <!--1ormorerepetitions:-->
        <string>id</string>
        <string>alias</string>
        </attributes>
       """
       #utilizar sempre o ALIAS para procurar o grupo
       response = request_ca(operation_name, body_xml)

       #with open("group_id.xml", "w") as f:
       #        f.write(response)
       
       try:
       
         parser = re.search(r"cnt:(.*?)&lt", str(response))
         group_id = parser.group(1)
       except:
         pass
         group_id = "5F009016BFC112479D118F80E24A0A8F"
       return group_id
       
       
def get_classification(sid, classification):


       operation_name = "doSelect"

       classification = str(classification)
       classification = classification.replace("['", "")
       classification = classification.replace("']", "")
       #print(str(group))
       body_xml = f"""
       <sid>{sid}</sid>
       <objectType>pcat</objectType>
       <whereClause>sym LIKE '%{classification}%'</whereClause>
       <maxRows>-1</maxRows>
       <attributes>
       <!--1ormorerepetitions:-->
        
        </attributes>
       """
       #utilizar sempre o ALIAS para procurar o grupo
       response = request_ca(operation_name, body_xml)

       with open("group_id.xml", "w") as f:
               f.write(response)
       
       try:
       
         parser = re.search(r"pcat:(.*?)&lt", str(response))
         pcat_id = parser.group(1)
       except:
         print("Pcat nao encontrado para classificacao")
         
       return "pcat:"+str(pcat_id)
       
       




def create_request(sid, user, resource_affected, summary, description, type_req):
        operation_name = "createRequest"
        
        #configura grupo / classificacao por alarme #####
        
        
          group_id = "5F009016BFC112479D118F80E24A0A8F"
        
        
        
        
        
        #Pega grupo correto
        group_id = get_group(sid, group)
        ###############
        
        
        #aguarda 3 segundos
        time.sleep(3)
        ##########
        
        #Pega classificacao correta
        
        classification = get_classification(sid, pcat)
        time.sleep(3)
        
        #aguarda 3 segundos apos pegar classificacao
        
        
        ##############################
        
        #aguarda 3 segundos apos pegar item de configuração
        
        id_resource = get_affected_resource(sid, resource)
        
        
        ##############################################
        
        
        time.sleep(3)

        user_id, origin_group = get_user_id(sid, user)
        #id_resource, solution_group = get_affected_resource(sid, resource_affected)
        
        try:
            r = re.search(r"<div>(.*?)</div></div>", description)
            description = r.group(1)
        except:
            description = description
            
        
        

        body_xml = f"""
        <sid>{sid}</sid>
        <creatorHandle>cnt:{user_id}</creatorHandle>
        <attrVals>
        <string>z_srl_GrupoOriginador</string>
        <string>{origin_group}</string>
        <string>category</string>
        <string>{classification}</string>
        <string>affected_resource</string>
        <string>{id_resource}</string>
        <string>group</string>
        <string>{group_id}</string>
        <string>customer</string>
        <string>{user_id}</string>
        <string>summary</string>
        <string>{summary}</string>
        <string>description</string>
        <string><![CDATA[{description}]]></string>
        <string>type</string>
        <string>{type_req}</string>
        </attrVals>
        <propertyValues></propertyValues>
        <template></template>
        <attributes></attributes>
        <newRequestHandle>?</newRequestHandle>
        <newRequestNumber>?</newRequestNumber>
        """

        response = request_ca(operation_name, body_xml)

        parsed = parsing_to_json(response)

        #ticket_handle = json.loads(parsed)['UDSObject']['Handle']

        #for attr in json.loads(parsed)['UDSObject']['Attributes']['Attribute']:
        #        if attr['AttrName'] == 'ref_num':
        #                ticket_number = attr['AttrValue']
        #nota = "Solicitação criada de número: "+str(ticket_number) + " Desc: " + str(description)
        return response
        
        #return ticket_handle, ticket_number






def create_activity_log(sid, user, handle_ticket, description, time):
        operation_name = "createActivityLog"

        body_xml = f"""
        <sid>{sid}</sid>
        <creator>{user}</creator>
        <objectHandle>{handle_ticket}</objectHandle>
        <description><![CDATA[{description}]]></description>
        <logType>LOG</logType>
        <timeSpent>{time}</timeSpent>
        <internal>1</internal>
        """

        response = request_ca(operation_name, body_xml)

        parsed = parsing_to_json(response)

        return parsed



if __name__ == "__main__":

        if os.path.exists("sid.txt"):
                last_modified = datetime.datetime.fromtimestamp(os.path.getmtime("sid.txt"))

                if datetime.datetime.now() - last_modified >= datetime.timedelta(hours=1):
                        login()

                with open("sid.txt", "r") as f:
                        sid = f.read()
        else:
                sid = login()


        parser = argparse.ArgumentParser(description='Exemplo de script usando argparse')
        #Argumentos para consulta de grupo
        
        parser.add_argument("--get_resources", nargs=1, metavar=('resource'), help="Consulta de classificacao")
        
        parser.add_argument("--get_classification", nargs=1, metavar=('classification'), help="Consulta de classificacao")
        
        
        parser.add_argument("--search_group", nargs=1, metavar=('group'), help="Consulta grupo usando doSelect()")
        
        # Argumentos para create_request
        parser.add_argument('--create_request', nargs=4, metavar=('resource', 'summary', 'description', 'request_type'), help='Cria uma solicitação usando create_request')

        # Argumentos para get_user_id
        parser.add_argument('--get_user_id', nargs=1, metavar=('username'), help='Obtém o ID do usuário usando get_user_id')

        # Argumentos para get_ticket
        parser.add_argument('--get_ticket', nargs=1, metavar=('ref_num'), help='Obtém o ticket usando get_ticket')

        # Argumentos para create_activity_log
        parser.add_argument('--create_activity_log', nargs=4, metavar=('username', 'handle_ticket', 'description', 'time'), help='Cria um registro de atividade usando create_activity_log')

        args = parser.parse_args()

        if args.create_request:
                resource, summary, description, request_type = args.create_request
                print(create_request(sid, "x", resource, summary, description, request_type))
        elif args.get_user_id:
                username = args.get_user_id
                print(get_user_id(sid, username))
        elif args.get_ticket:
                ref_num = args.get_ticket
                print(get_ticket(sid, ref_num))
        elif args.search_group:
                group = args.search_group
                print(get_group(sid, group))
        elif args.get_resources:
                resource = args.get_resources
                print(get_affected_resource(sid, resource))
        elif args.get_classification:
            classification = args.get_classification
            print(get_classification(sid, classification))
                
        elif args.create_activity_log:
                username, handle_ticket, description, time = args.create_activity_log
                print(create_activity_log(sid, username, handle_ticket, description, time))
        else:
                print('Nenhuma ação especificada.')
