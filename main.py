#
 # Copyright (c) 2023 - Freddy Rivero
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
#



import requests
import mysql.connector
from lxml import etree
from requests.exceptions import RequestException
from mysql.connector.errors import Error as MySQLConnectorError
import xml.etree.ElementTree as ET


def download_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except RequestException as e:
        print(f"Error downloading file: {e}")
        return None

def parse_ofac_sdn_list(xml_data):
    if xml_data is None:
        return []

    try:
        root = etree.fromstring(xml_data)
        sdn_entries = []

        for entry in root.xpath('//ns:sdnEntry', namespaces={'ns': 'http://tempuri.org/sdnList.xsd'}):
            sdn_entry = {
                'uid': entry.findtext('ns:uid', default='', namespaces={'ns': 'http://tempuri.org/sdnList.xsd'}),
                'firstName': entry.findtext('ns:firstName', default='', namespaces={'ns': 'http://tempuri.org/sdnList.xsd'}),
                'lastName': entry.findtext('ns:lastName', default='', namespaces={'ns': 'http://tempuri.org/sdnList.xsd'}),
            }
            sdn_entries.append(sdn_entry)

        return sdn_entries
    except etree.XMLSyntaxError as e:
        print(f"Error parsing OFAC SDN XML data: {e}")
        return [] 

def parse_un_consolidated_list_entities(xml_data):
    if xml_data is None:
        return []

    try:
        root = ET.fromstring(xml_data)
        consolidated_entities = []

        for entry in root.findall('.//ENTITY'):
            dataid = entry.find('DATAID')
            if dataid is not None and dataid.text is not None:
                dataid = dataid.text
            else:
                dataid = ''

            first_name = entry.find('FIRST_NAME')
            if first_name is not None and first_name.text is not None:
                first_name = first_name.text.strip()
            else:
                first_name = ''

            un_list_type = entry.find('UN_LIST_TYPE')
            if un_list_type is not None and un_list_type.text is not None:
                un_list_type = un_list_type.text.strip()
            else:
                un_list_type = ''

            listed_on = entry.find('LISTED_ON')
            if listed_on is not None and listed_on.text is not None:
                listed_on = listed_on.text.strip()
            else:
                listed_on = ''

            comments1 = entry.find('COMMENTS1')
            if comments1 is not None and comments1.text is not None:
                comments1 = comments1.text.strip()
            else:
                comments1 = ''

            city = entry.find('ENTITY_ADDRESS/CITY')
            if city is not None and city.text is not None:
                city = city.text.strip()
            else:
                city = ''

            country = entry.find('ENTITY_ADDRESS/COUNTRY')
            if country is not None and country.text is not None:
                country = country.text.strip()
            else:
                country = ''

            consolidated_entity = {
                'dataid': dataid,
                'firstname': first_name,
                'un_list_type': un_list_type,
                'listed_on': listed_on,
                'comments1': comments1,
                'city': city,
                'country': country,
            }
            consolidated_entities.append(consolidated_entity)

        return consolidated_entities
    except ET.ParseError as e:
        print(f"Error parsing UN Consolidated XML data: {e}")
        return []

def parse_un_consolidated_list(xml_data):
    if xml_data is None:
        return []

    try:
        root = ET.fromstring(xml_data)
        consolidated_entries = []

        for entry in root.findall('.//INDIVIDUAL'):
            dataid = entry.find('DATAID')
            if dataid is not None:
                dataid = dataid.text
            else:
                dataid = ''

            first_name = entry.find('FIRST_NAME')
            if first_name is not None and first_name.text is not None:
                first_name = first_name.text.strip()
            else:
                first_name = ''

            second_name = entry.find('SECOND_NAME')
            if second_name is not None and second_name.text is not None:
                second_name = second_name.text.strip()
            else:
                second_name = ''

            third_name = entry.find('THIRD_NAME')
            if third_name is not None and third_name.text is not None:
                third_name = third_name.text.strip()
            else:
                third_name = ''

            fourth_name = entry.find('FOURTH_NAME')
            if fourth_name is not None and fourth_name.text is not None:
                fourth_name = fourth_name.text.strip()
            else:
                fourth_name = ''

            consolidated_entry = {
                'dataid': dataid,
                'firstname': first_name,
                'secondname': second_name,
                'thirdname': third_name,
                'fourthname': fourth_name,
            }
            consolidated_entries.append(consolidated_entry)

        return consolidated_entries
    except ET.ParseError as e:
        print(f"Error parsing UN Consolidated XML data: {e}")
        return []

def truncate_table(table_name, db_config):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        sql = f"TRUNCATE TABLE {table_name}"
        cursor.execute(sql)
        connection.commit()
    except MySQLConnectorError as e:
        print(f"Error truncating table {table_name}: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def save_to_database(entries, table_name, db_config):
    cursor = None
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        for entry in entries:
            placeholders = ', '.join(['%s'] * len(entry))
            columns = ', '.join(entry.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(entry.values()))

        connection.commit()
    except MySQLConnectorError as e:
        print(f"Error saving data to the database: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'ofac',
        'use_pure' : True
    }

    # Download and parse OFAC SDN list in XML format
    ofac_sdn_url = "https://www.treasury.gov/ofac/downloads/sdn.xml"
    ofac_sdn_data = download_file(ofac_sdn_url)
    print(f"Downloaded OFAC SDN XML data: {ofac_sdn_data is not None}")
    ofac_sdn_entries = parse_ofac_sdn_list(ofac_sdn_data)

    # Truncate tables before saving data
    truncate_table('ofac_sdn', db_config)
    truncate_table('un_consolidated', db_config)
    truncate_table('un_consolidated_entities', db_config)

    # Save OFAC SDN entries to the database
    save_to_database(ofac_sdn_entries, 'ofac_sdn', db_config)
    print(f"{len(ofac_sdn_entries)} OFAC SDN entries saved to the database")

    # Download and parse UN Security Council Consolidated list in XML format
    un_consolidated_list_url = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
    un_consolidated_list_data = download_file(un_consolidated_list_url)
    print(f"Downloaded UN Consolidated XML data: {un_consolidated_list_data is not None}")
    un_consolidated_list_entries = parse_un_consolidated_list(un_consolidated_list_data)
    un_consolidated_list_entries_entities = parse_un_consolidated_list_entities(un_consolidated_list_data)

    # Save UN Consolidated list entries to the database
    save_to_database(un_consolidated_list_entries, 'un_consolidated', db_config)
    save_to_database(un_consolidated_list_entries_entities, 'un_consolidated_entities', db_config)
    print(f"{len(un_consolidated_list_entries)} UN Consolidated list entries saved to the database")
    print(f"{len(un_consolidated_list_entries_entities)} UN Consolidated list entities entries saved to the database")


if __name__ == "__main__":
    main()
