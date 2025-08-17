from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from typing import Final, List
from .utils import validate_json_file, load_blocks_from_json
import requests

#Constants
OLLAMA_URL: Final[str] = "http://localhost:11434"
VECTOR_SIZE: Final[int] = 768

class PersonalAIQdrantClient:
    def __init__(self, user_id: str, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.user_id = user_id

    def _get_collection_name(self, base_name: str) -> str:
        return f"{self.user_id}_{base_name}"

    def create_collection(self, collection_name: str, vector_size: int = VECTOR_SIZE) -> bool:
        """
        Creates a collection with the given name and vector size.

        Args:
            collection_name (str): The name of the collection to be created.
            vector_size (int, optional): The size of the vector. Defaults to 768.

        Raises:
            Exception: If the collection already exists or there is an error creating the collection.

        Prints:
            str: A message indicating if the collection was created or if it already exists.
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            print(f"Collection created:'{collection_name}'")
            return True
        except Exception as e:
            print(f"Collection already exist or Error: {e}")
            return False

    def get_embedding(self, text: str) -> List[float]:
        """
        Sends a POST request to the OLLAMA API to get the embedding for the given text.

        Args:
            text (str): The text for which the embedding is to be obtained.

        Returns:
            list: The embedding of the text.
        """
        try:
            response = requests.post(f'{OLLAMA_URL}/api/embeddings',
                json={
                    'model': 'nomic-embed-text',
                    'prompt': text
                })
            response.raise_for_status()
            return response.json()['embedding']
        except requests.RequestException as e:
            raise Exception(f"Ollama API Error: {e}")
        except KeyError:
            raise Exception("Unexpected Ollama API response")

    def upload_profile(self, json_file: str) -> bool:
        """
        Uploads profile blocks to the specified collection.

        Args:
            json_file (str): The path to the JSON file containing the profile blocks.
            collection_name (str): The name of the collection to which the profile blocks will be uploaded.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not validate_json_file(json_file):
                print(f"Error: '{json_file}' is not a valid JSON-file.")
                return False
        
            collection_name = self._get_collection_name("profile")
            self.create_collection(collection_name)

            blocks = load_blocks_from_json(json_file)

            points=[]
            for block in blocks:
                embedding = self.get_embedding(block["text"])
                points.append({
                    "id": block["id"],
                    "vector": embedding,
                    "payload": {
                        "text": block["text"],
                        "category": block["category"]
                    }
                })

            self.client.upsert(collection_name=collection_name, points=points)
            print(f"{len(points)} profile blocks uploaded.")
            return True
        except Exception as e:
            print(f"Error uploading profile: {e}")
            return False

    def setup_conversation_collection(self) -> bool:
        """
        Setup a collection for storing conversation data.

        Args:
            collection_name (str): The name of the collection to be created.

        Returns:
            bool: True if the collection was created successfully, False otherwise.

        Description:
            This function creates a collection with the given name and vector size and retrieves the number of points in the collection.
            If the collection creation is successful, it prints a message indicating the number of points in the collection and returns True.
            If there is an error creating the collection, it prints an error message and returns False.
        """
        collection_name = self._get_collection_name("conversations")
        try:
            self.create_collection(collection_name)

            info = self.client.get_collection(collection_name)
            print(f"Collection: '{collection_name}' ready: {info.points_count} points.")
            return True
        except Exception as e:
            print(f" error creating collection: '{collection_name}': {e}")
            return False
        
    def add_conversation(self, user_message: str, assistant_response: str) -> bool:
        collection_name = self._get_collection_name("conversations")
        try:
            full_text = f"{user_message} {assistant_response}"
            embedding = self.get_embedding(full_text)

            points = [{
                "vector": embedding,
                "payload": {
                    "type": "conversation",
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "timestamp": datetime.now().isoformat()
                }
            }]

            self.client.upsert(collection_name=collection_name, points=points)
            print(f"Conversation added to '{collection_name}'")
            return True
        except Exception as e:
            print(f"Error adding conversation: {e}")
            return False
        
    def search_similar(self, collection_type: str, query_text: str, limit: int = 3) -> List:
        try:
            collection_name = self._get_collection_name(collection_type)
            query_embedding = self.get_embedding(query_text)

            results = self.client.search(
                collection_name = collection_name,
                query_vector = query_embedding,
                limit = limit,
                with_payload = True
            )
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []