import os
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2 import sql, OperationalError, DatabaseError
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# Load BioBERT model and tokenizer for NER
model_name = "dmis-lab/biobert-base-cased-v1.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

# Directory containing XML files
xml_files_dir = "/Users/diana/Desktop/TT"

# Database queries
create_table_query = '''
CREATE TABLE IF NOT EXISTS Sentences (
    SentenceID SERIAL PRIMARY KEY,
    ArticleID TEXT,
    Subdomain TEXT,
    SentenceText TEXT
);
'''

create_entities_table_query = '''
CREATE TABLE IF NOT EXISTS Entities (
    EntityID SERIAL PRIMARY KEY,
    SentenceID INTEGER REFERENCES Sentences(SentenceID),
    EntityText TEXT,
    EntityType TEXT
);
'''

insert_sentence_query = '''
INSERT INTO Sentences (ArticleID, Subdomain, SentenceText) 
VALUES (%s, %s, %s) RETURNING SentenceID;
'''

insert_entity_query = '''
INSERT INTO Entities (SentenceID, EntityText, EntityType) 
VALUES (%s, %s, %s);
'''

# Processing and inserting XML data
def process_xml_files(xml_files_dir, cursor):
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
                        subdomain = umlsterm.attrib.get('preferred', '')
                        sentence_text = ''.join(sentence.itertext()).strip() if sentence.text is None else sentence.text.strip()

                        # Insert sentence data into PostgreSQL
                        cursor.execute(insert_sentence_query, (article_id, subdomain, sentence_text))
                        sentence_id = cursor.fetchone()[0]

                        # Perform NER using BioBERT
                        ner_results = ner_pipeline(sentence_text)
                        for ent in ner_results:
                            cursor.execute(insert_entity_query, (sentence_id, ent['word'], ent['entity']))
                
                conn.commit()
            except ET.ParseError as e:  # XML syntax problems
                print(f"ParseError in file {xml_file}: {e}")
            except DatabaseError as e:  # Database-related problems
                print(f"DatabaseError occurred with file {xml_file}: {e}")
                conn.rollback()  # Rollback in case of error
            except Exception as e:  # Other problems
                print(f"An error occurred with file {xml_file}: {e}")
                conn.rollback()  # Rollback in case of error
        else:
            print(f"Skipping file: {xml_file}, it's either not a file or empty.")

# Main execution
def main():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        cursor = conn.cursor()

        # Create tables
        cursor.execute(create_table_query)
        cursor.execute(create_entities_table_query)
        conn.commit()

        # Process XML files
        process_xml_files(xml_files_dir, cursor)

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

if __name__ == "__main__":
    main()
