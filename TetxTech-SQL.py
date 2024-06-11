import os
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2 import sql, OperationalError, DatabaseError

# Database connection parameters
db_params = {
    'dbname': 'your_database',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'your_host',
    'port': 5432  # Ensure this is an integer
}

# Directory containing XML files
xml_files_dir = "/Users/diana/Desktop/TT"

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS Sentences (
        SentenceID SERIAL PRIMARY KEY,
        ArticleID TEXT,
        Subdomain TEXT,
        SentenceText TEXT
    );
    '''
    cursor.execute(create_table_query)
    conn.commit()

    # XML filenames with dir
    xml_filenames = [os.path.join(xml_files_dir, filename) for filename in os.listdir(xml_files_dir)]

    for xml_file in xml_filenames:
        if os.path.isfile(xml_file) and os.path.getsize(xml_file) > 0:  # Ensure it's a file and it's not empty
            try:
                print(f"Processing file: {xml_file}")
                tree = ET.parse(xml_file)
                root = tree.getroot()

                article_id = root.attrib.get('id')  # unique article's identification

                for sentence in root.findall('.//sentence'):
                    umlsterm = sentence.find('.//umlsterm/concept')
                    if umlsterm is not None:  # sometimes subdomains are missing
                        subdomain = umlsterm.attrib.get('preferred', '').replace("'", "''")
                        sentence_text = ''.join(sentence.itertext()).strip().replace("'", "''") if sentence.text is None else sentence.text.strip().replace("'", "''")

                        # Insert data into PostgreSQL
                        insert_query = '''
                        INSERT INTO Sentences (ArticleID, Subdomain, SentenceText) 
                        VALUES (%s, %s, %s);
                        '''
                        cursor.execute(insert_query, (article_id, subdomain, sentence_text))
                        conn.commit()
            except ET.ParseError as e:  # just checking if any XML syntax problems are there hindering parsing
                print(f"ParseError in file {xml_file}: {e}")
            except DatabaseError as e:  # any database-related problems
                print(f"DatabaseError occurred with file {xml_file}: {e}")
                conn.rollback()  # Rollback in case of error
            except Exception as e:  # any other problems
                print(f"An error occurred with file {xml_file}: {e}")
                conn.rollback()  # Rollback in case of error
        else:
            print(f"Skipping file: {xml_file}, it's either not a file or empty.")

except OperationalError as e:
    print(f"Error connecting to the database: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Ensure the database connection is closed
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn:
        conn.close()

print("Data extraction and insertion into PostgreSQL complete.")
