import os
import chromadb

# Ensure chroma stores locally
os.makedirs("memory/vector_db", exist_ok=True)
client = chromadb.PersistentClient(path="memory/vector_db")

try:
    collection = client.get_or_create_collection(name="tasks")
except Exception:
    # Fallback if ChromaDB needs reinitialization
    client.delete_collection(name="tasks")
    collection = client.create_collection(name="tasks")

def embed_task(task_id, user_input, plan):
    """Store a completed task in the vector database"""
    summary = f"Task: {user_input}\nPlan: {plan}"
    collection.add(
        documents=[summary],
        metadatas=[{"task_id": task_id}],
        ids=[task_id]
    )

def search_tasks(query, n_results=1):
    """Search for relevant past tasks"""
    if collection.count() == 0:
        return []
    
    # ensure n_results does not exceed count
    n = min(n_results, collection.count())
    results = collection.query(query_texts=[query], n_results=n)
    
    if results and results["documents"] and results["documents"][0]:
        return results["documents"][0]
    return []
