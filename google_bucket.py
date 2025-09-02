from google.cloud import storage


def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """
    Uploads a file to the Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of your GCS bucket.
        source_file_path (str): The full path to the file on your local machine.
        destination_blob_name (str): The desired name of the object (file) in the GCS bucket.
                                     This can include a path-like prefix, e.g., 'my_folder/my_file.txt'.
    """
    try:
        # Initialize a client. The client will automatically use your ADC credentials.
        storage_client = storage.Client()

        # Get a reference to the bucket
        bucket = storage_client.bucket(bucket_name)

        # Create a blob object for the destination file in the bucket
        blob = bucket.blob(destination_blob_name)

        # Upload the file from the local path
        blob.upload_from_filename(source_file_path)

        print(f"File '{source_file_path}' uploaded to '{bucket_name}/{destination_blob_name}' successfully.")

    except Exception as e:
        print(f"An error occurred during upload: {e}")
        print("Please ensure your environment is authenticated and you have write permissions to the bucket.")

# --- Configuration ---
YOUR_BUCKET_NAME = "your-gcs-bucket-name"  # Replace with the name of your bucket
LOCAL_FILE_PATH = "path/to/your/local_file.txt" # Replace with the full path to your local file
# Example: LOCAL_FILE_PATH = "/Users/youruser/Documents/my_important_data.csv"
# Example: LOCAL_FILE_PATH = "C:\\Users\\youruser\\Documents\\report.pdf"

# The name you want the file to have in the bucket.
# You can also include a 'folder' structure, e.g., 'reports/january/data.csv'
DESTINATION_BLOB_NAME = "uploaded_file_name.txt"

# --- Call the function to perform the upload ---
# First, let's create a dummy file for demonstration if it doesn't exist
if not os.path.exists(LOCAL_FILE_PATH):
    print(f"Creating dummy file: {LOCAL_FILE_PATH}")
    os.makedirs(os.path.dirname(LOCAL_FILE_PATH) or '.', exist_ok=True)
    with open(LOCAL_FILE_PATH, 'w') as f:
        f.write("This is some sample content for the uploaded file.\n")
        f.write("Another line of content.\n")
    print("Dummy file created. Now attempting upload.")

upload_to_gcs(YOUR_BUCKET_NAME, LOCAL_FILE_PATH, DESTINATION_BLOB_NAME)

# You can also upload another file:
# upload_to_gcs(YOUR_BUCKET_NAME, "path/to/another_image.jpg", "images/new_image.jpg")
