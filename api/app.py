import os
import time
from flask import Flask, request, jsonify
import weaviate
from sentence_transformers import SentenceTransformer

WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://weaviate:8080")

app = Flask(__name__)

# Weaviate client
client = weaviate.Client(url=WEAVIATE_URL)

# Wait for Weaviate to be ready
for i in range(10):
    try:
        client.schema.get()
        print("Weaviate ready")
        break
    except Exception:
        print("Waiting for Weaviate...")
        time.sleep(2)

# Load SentenceTransformer once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

CLASS_NAME = "Sentence"

def ensure_schema(retries=10, delay=2):
    """Ensure that the class exists in Weaviate, retrying if Weaviate is not ready."""
    for _ in range(retries):
        try:
            schema = client.schema.get()
            class_names = [c["class"] for c in schema.get("classes", [])]
            if CLASS_NAME in class_names:
                return
            # Class doesn't exist -> create it
            new_class = {
                "class": CLASS_NAME,
                "description": "Sentences and their vectors",
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "meta", "dataType": ["text"]},
                ],
            }
            client.schema.create_class(new_class)
            return
        except Exception as e:
            print(f"Weaviate not ready, retrying in {delay}s... ({e})")
            time.sleep(delay)
    raise RuntimeError("Weaviate schema could not be ensured after retries.")

ensure_schema()

@app.route("/ingest", methods=["POST"])
def ingest():
    payload = request.json
    if not payload:
        return jsonify({"error": "JSON body required"}), 400

    embedding = payload.get("embedding")
    text = payload.get("text", "")
    meta = payload.get("meta", {})

    if embedding is None:
        if not text:
            return jsonify({"error": "text required if no embedding provided"}), 400
        embedding = model.encode([text])[0].tolist()

    obj = {"text": text, "meta": str(meta)}
    try:
        client.data_object.create(obj, CLASS_NAME, vector=embedding)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 201

@app.route("/query", methods=["POST"])
def query():
    payload = request.json or {}
    embedding = payload.get("embedding")
    text = payload.get("text", "")

    if embedding is None:
        if not text:
            return jsonify({"error": "text or embedding required"}), 400
        embedding = model.encode([text])[0].tolist()

    try:
        res = client.query.get(CLASS_NAME, ["text", "meta"]) \
            .with_near_vector({"vector": embedding}) \
            .with_limit(10) \
            .do()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    matches = []
    try:
        for entry in res["data"]["Get"][CLASS_NAME]:
            matches.append(entry)
    except Exception:
        matches = res

    return jsonify({"results": matches})

@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint"""
    try:
        # Check if Weaviate is accessible
        client.schema.get()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


