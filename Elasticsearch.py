# Extension of the project from sql table to a more advanced searching tool Elasticsearch

import pandas as pd
from sqlalchemy import create_engine
from elasticsearch_dsl import Index, Document, Text, Keyword, connections, Search, Q


# Connecting to Elasticsearch
connections.create_connection(hosts=['http://localhost:9200'])

# Defining the document structure
class Abstract(Document):
    article_id = Keyword()
    keywords = Text()
    abstracts = Text()     
    
    class Index:
        name = 'abstracts'  

# Create the index if it doesn't exist
if not Abstract._index.exists():
    Abstract.init() 

# Fetching the data from the SQL database

DB_USERNAME = 'diana'  
DB_HOST = 'localhost'
DB_PORT = '5432' 
DB_NAME = 'SQL_Database'

db_url = f'postgresql+psycopg2://{DB_USERNAME}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url) #connecting to the SQL database

# Fetch the articleids, keywords and abstracts data
df = pd.read_sql('SELECT ArticleID as article_id, Keywords as keywords, Abstracts as abstracts FROM Sentences', engine)

# Index the data in Elasticsearch
for _, row in df.iterrows():
    abstract = Abstract(
        meta={'id': row['article_id']},
        article_id=row['article_id'],
        keywords=row['keywords'],
        abstracts=row['abstracts']
    )
    abstract.save()  # Saving the document in the Elasticsearch index

# Defining a search function with highlighting and scoring
def search_keywords(query):
    s = Search(index='abstracts').query(
        Q('multi_match', query=query, fields=['keywords', 'abstracts'], operator='and')
    ).highlight('abstracts', fragment_size=50)
    
    response = s.execute()  # Execute the search query
    
    results = []
    for match in response:
        highlights = match.meta.highlight.abstracts if 'highlight' in match.meta else []
        result = {
            'article_id': match.article_id,
            'score': match.meta.score,
            'highlights': highlights
        }
        results.append(result)
    return results

# Example search query

if __name__ == "__main__":
    query = 'A  significant  correlation between'  # The term to search for
    results = search_keywords(query)
    for result in results:
        print(f"Found document ID: {result['article_id']}")
        print(f"Score: {result['score']}")
        print("Highlights:")
        for highlight in result['highlights']:
            print(highlight)
