# ofac
### Sanctioned Entities Parser

**This Python script downloads, parses, and saves OFAC SDN and UN Security Council Consolidated lists to a MySQL database.**

## Features

- Downloads OFAC SDN list in XML format
- Parses OFAC SDN list and extracts relevant information
- Downloads UN Security Council Consolidated list in XML format
- Parses UN Security Council Consolidated list and extracts relevant information
- Saves the extracted data into a MySQL database

## Dependencies

The script requires the following Python libraries:

- requests
- lxml
- mysql-connector-python

You can install these dependencies using pip:

```pip install requests lxml mysql-connector-python```

## Usage

1. Set up a MySQL database and create the necessary tables. An example schema can be found below.

2. Edit the db_config dictionary in the main() function with your MySQL database credentials.

3. Run the script:

```python sanctioned_entities_parser.py```

## Example Database Schema

The following is an example of a database schema for the tables ofac_sdn, un_consolidated, and un_consolidated_entities.

```
CREATE TABLE ofac_sdn (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255),
    firstName VARCHAR(255),
    lastName VARCHAR(255)
);

CREATE TABLE un_consolidated (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataid VARCHAR(255),
    firstname VARCHAR(255),
    secondname VARCHAR(255),
    thirdname VARCHAR(255),
    fourthname VARCHAR(255)
);

CREATE TABLE un_consolidated_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataid VARCHAR(255),
    firstname VARCHAR(255),
    un_list_type VARCHAR(255),
    listed_on VARCHAR(255),
    comments1 VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255)
);
```

## License

This project is licensed under the MIT License.

