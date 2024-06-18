import os
import xml.etree.ElementTree as ET

# Define file paths and translations
xml_files_dir = "/Users/diana/Desktop/TT"
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

# Create SQL file and write table creation statement
with open(output_sql_file, 'w') as f:
    f.write('''CREATE TABLE IF NOT EXISTS Sentences (
                    ArticleID TEXT,
                    Subdomain TEXT,
                    Keywords TEXT
                 );\n''')

    # Iterate through XML files in the specified directory
    for filename in os.listdir(xml_files_dir):
        xml_file_path = os.path.join(xml_files_dir, filename)

        if os.path.isfile(xml_file_path) and os.path.getsize(xml_file_path) > 0:
            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                article_id = root.attrib.get('id')
                subdomain = os.path.splitext(filename)[0]

                # Translate subdomain if possible
                subdomain_translation = subdomain_translations.get(subdomain, subdomain)

                # Extract keywords
                concepts = [concept.attrib['preferred'] for concept in root.findall('.//concept') if
                            'preferred' in concept.attrib]
                keywords = ', '.join(concepts).replace("'", "''")  # Escape single quotes

                # Write article ID, subdomain, and keywords to SQL file
                f.write(
                    f"INSERT INTO Sentences (ArticleID, Subdomain, Keywords) VALUES ('{article_id}', '{subdomain_translation}', '{keywords}');\n")

            except ET.ParseError:
                print(f"Error parsing XML file: {xml_file_path}")
            except Exception as e:
                print(f"Unexpected error processing file {xml_file_path}: {e}")

print("Data extraction and SQL creation complete.")
