from google import genai
import vertexai
from dotenv import load_dotenv
from vertexai import rag
load_dotenv()
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
# Use the environment variable if the user doesn't provide Project ID.
from google.cloud import storage
import os 



PROJECT_ID =os.getenv("GOOGLE_CLOUD_PROJECT")
# if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
#     PROJECT_ID = str(os.environ.get("GOOGLE_CLOUD_PROJECT"))

LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
rag_corpus=rag.get_corpus(os.getenv('RAG_CORPUS'))




class VertexRAGToolSchema(BaseModel):
    """Input for Vertex RAG Tool."""
    query: str = Field(..., description="The query to search the RAG corpus.")

def download_gcs_file(bucket_name, source_blob_name, destination_file_path):
    """
    Downloads a blob (file) from a Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of your GCS bucket.
        source_blob_name (str): The full path to the file in the GCS bucket.
                                 This is often just the file name, but can include
                                 a 'folder' path like 'documents/my_file.pdf'.
        destination_file_path (str): The full path on your local machine where
                                     the downloaded file will be saved.
    """
    try:
        # Initialize a client. The client will automatically use your ADC credentials.
        storage_client = storage.Client()

        # CORRECTED: Use the bucket_name argument instead of hardcoding
        bucket = storage_client.bucket(bucket_name)

        # Create a blob object for the source file in the bucket
        blob = bucket.blob(source_blob_name)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

        # Download the file to the specified local path
        blob.download_to_filename(destination_file_path)

        print(f"File '{source_blob_name}' downloaded to '{destination_file_path}' successfully.")

    except Exception as e:
        print(f"An error occurred during download of '{source_blob_name}': {e}")
        print("Possible reasons for failure:")
        print("1. The bucket or file does not exist, or the name is incorrect.")
        print("2. Your authenticated account does not have 'storage.objects.get' permission for the file.")
        print("3. Check your internet connection or network configuration.")
        print("-" * 30) # Separator for easier readability if multiple errors


class VertexRAGTool(BaseTool):
    """A tool to query a Vertex RAG corpus that contains documents related to CEMEX"""
    name: str = "Vertex RAG Tool"
    description: str = (
        "This tool queries a Vertex RAG corpus using a provided query. "
        "It returns relevant documents from the corpus."
    )
    args_schema: Type[BaseModel] = VertexRAGToolSchema

    def _run(self, query: str) -> Dict[str, Any]:
        """Run the RAG query and return the results."""
        try:
            response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=rag_corpus.name,
                    # Optional: supply IDs from `rag.list_files()`.
                    # rag_file_ids=["rag-file-1", "rag-file-2", ...],
                )
            ],
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=10,  # Optional
                filter=rag.Filter(
                    vector_distance_threshold=0.5,  # Optional
                ),
            ),
            text=query,
            )  # The query text to search in the RAG corpus
           
            links = []
            if response and response.contexts and response.contexts.contexts: # Accessing the list of Context objects
                for context in response.contexts.contexts: # Iterate through each context object
                    if hasattr(context, 'source_display_name') and context.source_display_name:
                        links.append(context.source_display_name)
                    elif hasattr(context, 'source') and hasattr(context.source, 'source_display_name') and context.source.source_display_name:
                        # Depending on the exact structure, source_display_name might be nested under 'source'
                        links.append(context.source.source_display_name)


            file_name= set(links) # Convert to a set to remove duplicates
            # --- Configuration ---
            GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME') 
            LOCAL_DOWNLOAD_DIRECTORY = r"D:\\Crewai Projects\\cemex\\bucket_files" 

            # --- Loop through each file and download it ---
            # print(f"Starting download of {len(file_name)} files from '{GCS_BUCKET_NAME}' to '{LOCAL_DOWNLOAD_DIRECTORY}'")
            for file_name in file_name:
                # Construct the full local destination path for the current file
                local_destination_path = os.path.join(LOCAL_DOWNLOAD_DIRECTORY, file_name)

                # Call the download function for each file
                download_gcs_file(GCS_BUCKET_NAME, file_name, local_destination_path)


            return response
        except Exception as e:
            return {"error": str(e)}
    

# if __name__ == "__main__":
#     tool = VertexRAGTool()
#     query = "how to fix the wall cracks in a building?"
#     result = tool._run(query=query)
#     print(result)



