import os
import glob
from lxml import etree
import matplotlib.pyplot as plt

# Define the path to the XSD schema and the directory containing the XML files
current_dir = os.path.dirname(os.path.abspath(__file__))
xsd_path = os.path.join(current_dir, 'doc_validation.xsd')
xml_dir = os.path.join(current_dir, 'xmlV4.2_train')  # Updated to point to the xmlV4.2_train directory

# Debug information
print(f"Current directory: {current_dir}")
print(f"XSD path: {xsd_path}")
print(f"XML directory: {xml_dir}")

# List all files in the XML directory to check if XML files exist and have the correct extension
all_files = os.listdir(xml_dir)
print(f"All files in the XML directory: {all_files}")

# Load the XSD schema
try:
    with open(xsd_path, 'rb') as xsd_file:
        schema_root = etree.XML(xsd_file.read())
    schema = etree.XMLSchema(schema_root)
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)

# Create an XML parser with the schema
parser = etree.XMLParser(schema=schema)

# Validate all XML files in the directory
xml_files = glob.glob(os.path.join(xml_dir, '*.xml'))
print(f"Found {len(xml_files)} XML files: {xml_files}")

valid_files = []
invalid_files = []

for xml_file in xml_files:
    try:
        with open(xml_file, 'rb') as file:
            doc = etree.parse(file, parser)
        valid_files.append(xml_file)
    except (etree.XMLSyntaxError, etree.DocumentInvalid, UnicodeDecodeError) as e:
        invalid_files.append((xml_file, str(e)))

# Print the results
print(f"Valid XML files: {len(valid_files)}")
print(f"Invalid XML files: {len(invalid_files)}")

if invalid_files:
    print("\nList of invalid files and errors:")
    for file, error in invalid_files:
        print(f"{file}: {error}")

# Create a chart of the validation results
fig, ax = plt.subplots()
ax.barh(['Valid', 'Invalid'], [len(valid_files), len(invalid_files)], color=['green', 'red'])
ax.set_xlabel('Number of Files')
ax.set_title('XML Validation Results')
plt.savefig('validation_results.png')
plt.show()