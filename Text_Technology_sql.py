import os
import xml.etree.ElementTree as ET

xml_files = "/Users/diana/Desktop/TT"
output_sql_file = 'sentences.sql'

with open(output_sql_file, 'w') as f:
    f.write('''CREATE TABLE IF NOT EXISTS Sentences (
                    SentenceID SERIAL PRIMARY KEY,
                    ArticleID TEXT,
                    Subdomain TEXT,
                    SentenceText TEXT
                 );\n''')

    # XML filenames with dir
    xml_filenames = [os.path.join(xml_files, filename) for filename in os.listdir(xml_files)]

    for xml_file in xml_filenames:
        if os.path.isfile(xml_file) and os.path.getsize(xml_file) > 0:  # Ensure it's a file and it's not empty
            try:
                print(f"Processing file: {xml_file}") 
                tree = ET.parse(xml_file)  
                root = tree.getroot()

                article_id = root.attrib.get('id') #unique article's identification

                for sentence in root.findall('.//sentence'):
                    umlsterm = sentence.find('.//umlsterm/concept')
                    if umlsterm is not None: #sometimes subdomains are missing
                        subdomain = umlsterm.attrib.get('preferred', '').replace("'", "''")  # Handle single quotes
                        sentence_text = ''.join(sentence.itertext()).strip().replace("'", "''") if sentence.text is None else sentence.text.strip().replace("'", "''")
                        f.write(f"INSERT INTO Sentences (ArticleID, Subdomain, SentenceText) VALUES ('{article_id}', '{subdomain}', '{sentence_text}');\n")
            except ET.ParseError as e: # just checking if any XML syntax problems are there hindering parsing
                print(f"ParseError in file {xml_file}: {e}") 
            except Exception as e: #any other problems
                print(f"An error occurred with file {xml_file}: {e}")
        else:
            print(f"Skipping file: {xml_file}, it's either not a file or empty.")

print("Data extraction and SQL creation complete.")


