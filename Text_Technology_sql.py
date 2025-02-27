import os
import xml.etree.ElementTree as ET

xml_files = "/Users/diana/Desktop/TT"
output_sql_file = 'sentences.sql'

subdomain_translations = {
    "Gefaesschirurgie": "Vascular Surgery",
    "DerInternist": "The Internist",
    "DerUnfallchirurg": "The Trauma Surgeon",
    "DerRadiologe": "The Radiologist",
    "DerNervenarzt": "The Neurologist",
    "HNO": "ENT (Ear, Nose, Throat)",
    "IntensiveMedizin": "Intensive Medicine",
    "DerHautarzt": "The Dermatologist",
    "EthikInDerMedizin": "Ethics in Medicine",
    "ZfuerHerzThoraxGefaesschirurgie": "Journal for Heart, Thorax and Vascular Surgery",
    "DerOpthalmologe": "The Ophthalmologist",
    "DerChirurg": "The Surgeon",
    "OperativeOrthopaedie": "Operative Orthopedics",
    "DerOrthopaede": "The Orthopedist",
    "Psychotherapeut": "Psychotherapist",
    "Herz": "Heart",
    "PerinatalMedizin": "Perinatal Medicine",
    "ZfuerGerontologie+Geriatrie": "Journal for Gerontology and Geriatrics",
    "ZfuerKardiologie": "Journal for Cardiology",
    "Reproduktionsmedizin": "Reproductive Medicine",
    "MedizinischeKlinik": "Medical Clinic",
    "KlinischeNeuroradiologie": "Clinical Neuroradiology",
    "DerAnaesthesist": "The Anesthetist",
    "DerGynaekologe": "The Gynecologist",
    "MundKieferGesichtschirurgie": "Oral and Maxillofacial Surgery",
    "ZfuerRheumatologie": "Journal for Rheumatology",
    "ForumDerPsychoanalyse": "Forum for Psychoanalysis",
    "Arthroskopie": "Arthroscopy",
    "Bundesgesundheitsblatt": "Federal Health Bulletin",
    "Strahlentherapie+Onkologie": "Radiotherapy and Oncology",
    "Rechtsmedizin": "Forensic Medicine",
    "ManuelleMedizin": "Manual Medicine",
    "DerUrologeA": "The Urologist A",
    "Trauma+Berufskrankheit": "Trauma and Occupational Disease",
    "Herzschrittmachertherapie": "Pacemaker Therapy",
    "MonatsschriftKinderheilkunde": "Monthly Journal of Pediatrics",
    "DerSchmerz": "The Pain",
    "Notfall+Rettungsmedizin": "Emergency and Rescue Medicine",
    "DerPathologe": "The Pathologist",
}
with open(output_sql_file, 'w') as f:
    f.write('''CREATE TABLE IF NOT EXISTS Sentences (
                    ArticleID TEXT,
                    Subdomain TEXT,
                    Keywords TEXT
                 );\n''')

    # XML filenames with dir
    xml_filenames = [os.path.join(xml_files, filename) for filename in os.listdir(xml_files)]

    for xml_file in xml_filenames:
        if os.path.isfile(xml_file) and os.path.getsize(xml_file) > 0:  # Ensure it's a file and it's not empty
            tree = ET.parse(xml_file)
            root = tree.getroot()
            article_id = root.attrib.get('id')
            subdomain = os.path.basename(xml_file).split('.')[0]
            
            # Translate subdomain if possible
            subdomain_translation = subdomain_translations.get(subdomain, subdomain)
            
            # Extract keywords
            concepts = [concept.attrib['preferred'] for concept in root.findall('.//concept') if 'preferred' in concept.attrib]
            #print (concepts)
            keywords = ', '.join(concepts).replace("'", "''")  # Escape single quotes

            # Write article ID, subdomain, and keywords to SQL file
            f.write(f"INSERT INTO Sentences (ArticleID, Subdomain, Keywords) VALUES ('{article_id}', '{subdomain_translation}', '{keywords}');\n")


print("Data extraction and SQL creation complete.")
            
"""article_sentences = []

            for sentence in root.findall('.//sentence'):
                text_element = sentence.find('.//text')
                if text_element is not None:
                    sentence_text = ' '.join(token.text for token in text_element.findall('.//token') if token.text)
                    sentence_text = sentence_text.replace("'", "''")  # Escape single quotes in the sentence text
                    article_sentences.append(sentence_text)

            for sentence_text in article_sentences:
                f.write(f"INSERT INTO Sentences (ArticleID, Subdomain, SentenceText) VALUES ("
                        f"'{article_id}', '{subdomain_translation}', '{sentence_text}');\n")"""

                    





