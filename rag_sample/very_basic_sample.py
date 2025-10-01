"""
Full example: Astra DB + OpenAI embeddings
Vectors stored and retrieved as float arrays in $vector (not $binary)
"""

import os
from astrapy import DataAPIClient
from astrapy.api_options import APIOptions, SerdesOptions
from astrapy.info import CollectionDefinition, CollectionVectorOptions
from astrapy.constants import VectorMetric
from openai import OpenAI


# -----------------------
# 1. Config
# -----------------------
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]  # e.g. "https://<id>-<region>.apps.astra.datastax.com"
ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

COLLECTION_NAME = "docs_openai_vectors_2"

# -----------------------
# 2. Astra client with serdes options
# -----------------------
opts = APIOptions(
    serdes_options=SerdesOptions(
        binary_encode_vectors=False,       # write: send vectors as float[] not $binary
        custom_datatypes_in_reading=False  # read: return Python list not DataAPIVector
    )
)

client = DataAPIClient(api_options=opts)
db = client.get_database(ASTRA_DB_API_ENDPOINT, token=ASTRA_DB_APPLICATION_TOKEN)

# -----------------------
# 3. Create vector-enabled collection (if not exists)
# -----------------------
definition = CollectionDefinition(
    vector=CollectionVectorOptions(
        dimension=1536,              # match embedding model
        metric=VectorMetric.COSINE
    )
)
col = db.create_collection(COLLECTION_NAME, definition=definition)

# -----------------------
# 4. Embed with OpenAI
# -----------------------
oai = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "text-embedding-3-small"

def embed(text: str):
    return oai.embeddings.create(model=MODEL, input=text).data[0].embedding

# -----------------------
# 5. Insert docs with $vector
# -----------------------
docs = [
    {"_id": "1", "text": "A guide to installing routers",      "$vector": embed("A guide to installing routers")},
    {"_id": "2", "text": "Troubleshooting home Wi-Fi issues",  "$vector": embed("Troubleshooting home Wi-Fi issues")},
    {"_id": "3", "text": "Mesh networks explained",            "$vector": embed("Mesh networks explained")},
]
col.insert_many(docs)

# -----------------------
# 6. Query with vector search
# -----------------------
qvec = embed("How to fix slow Wi-Fi at home?")
results = col.find({}, sort={"$vector": qvec}, limit=3, include_similarity=True, projection={"text": True, "$vector": True})

print("\n--- Results ---")
for r in results:
    print(f'{r["_id"]}: {r["text"]}  sim={r["$similarity"]:.4f}')
    print(f'  vector length: {len(r["$vector"])}; first 5 dims: {r["$vector"][:5]}')