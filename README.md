# CEMEX Damage Analysis Assistant

This project is a sophisticated AI-powered tool designed to assist in the analysis of structural damage. By leveraging a combination of multimodal AI agents, it can process both text queries and image uploads to provide detailed damage assessments and actionable repair guides. The application is built with a Streamlit front-end, making it interactive and user-friendly.

## Overview

At its core, the system uses the CrewAI framework to orchestrate a team of specialized AI agents. These agents collaborate to perform tasks such as visual inspection, damage diagnosis, and solution retrieval from a knowledge base, including CEMEX-specific documentation.

---

## Features

- **Multimodal Analysis:** Accepts both text-based queries and image uploads for comprehensive damage assessment.
- **AI Agent Crew:** Utilizes a team of specialized AI agents for:
  - **Damage Diagnosis:** Identifies structural elements and assesses damage from images.
  - **Solution Retrieval:** Recommends repair solutions and relevant CEMEX products.
  - **Report Generation:** Creates detailed and actionable repair guides.
- **Interactive Web Interface:** A user-friendly Streamlit application for easy interaction.
- **Google Cloud Integration:** Leverages Google Cloud Storage for document retrieval and Vertex AI for Retrieval-Augmented Generation (RAG).
- **Extensible Framework:** The use of CrewAI allows for easy extension with new agents and tools.

---

## Project Structure

```
.
├── app.py                  # Main Streamlit web application
├── crew.py                 # Defines the CrewAI agents and tasks
├── agents.yaml             # Configuration for the AI agents (roles, goals, backstories)
├── tasks.yaml              # Configuration for the tasks performed by the agents
├── vertex_rag_tool.py      # Custom tool for interacting with Google Vertex AI RAG
├── VisionTool.py           # Custom tool for image analysis using a vision model
├── google_bucket.py        # Helper script for Google Cloud Storage operations
└── ...                     # Other project files
```

---

## How It Works

The application orchestrates a workflow using a "crew" of AI agents, each with a specific role.

1. **Input:** The user provides a query and optionally uploads an image of the structural damage via the Streamlit interface.
2. **Damage Diagnostic Expert (`damage_diagnostic_expert`):** If an image is provided, this agent analyzes it using the VisionTool to identify the structural components and diagnose the type and severity of the damage.
3. **Repair Solution Specialist (`repair_solution_specialist`):** This agent takes the diagnosis report or the user's text query and uses the VertexRAGTool and SerperDevTool to search for appropriate repair solutions. It queries a knowledge base of documents (likely stored in Google Cloud Storage and indexed by Vertex AI RAG) to find relevant CEMEX products and repair procedures.
4. **Repair Guide Writer (`repair_guide_writer`):** The final agent synthesizes all the gathered information—the damage report, the retrieved solutions, and the original user query—to generate a comprehensive and easy-to-understand repair guide.
5. **Output:** The final report is displayed to the user in the Streamlit application.

---

## Getting Started

### Prerequisites

- Python 3.8+
- An OpenAI API Key
- A Serper API Key
- Access to a Google Cloud Platform project with Vertex AI and Google Cloud Storage enabled.
- Credentials for Google Cloud Platform (e.g., set up via `gcloud auth application-default login`)

### Installation

1. Clone the repository:
    ```sh
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file would need to be created based on the imports in the Python files.)*

3. Set up your environment variables:
    Create a `.env` file in the root of the project and add the following:
    ```
    OPENAI_API_KEY=\"your_openai_api_key\"
    SERPER_API_KEY=\"your_serper_api_key\"
    GOOGLE_CLOUD_PROJECT=\"your-gcp-project-id\"
    GOOGLE_CLOUD_REGION=\"your-gcp-region\"
    RAG_CORPUS=\"your-rag-corpus-id\"
    GCS_BUCKET_NAME=\"your-gcs-bucket-name\"
    ```

---

## Running the Application

To run the Streamlit application, execute the following command in your terminal:

```sh
streamlit run app.py
```

This will start a local web server, and you can access the application through your browser at the provided URL (usually http://localhost:8501).

---

## Configuration

- **agents.yaml:** This file defines the roles, goals, and backstories for each AI agent in the crew. You can modify this file to change the behavior and expertise of the agents.
- **tasks.yaml:** This file outlines the specific tasks that the agents will perform. You can adjust the descriptions and expected outputs to fine-tune the workflow.

---

## Tools

- **VisionTool.py:** A custom tool that leverages a multimodal model (like GPT-4o) to analyze images. It can take an image path and a query to return a textual description or answer questions about the image.
- **vertex_rag_tool.py:** This tool connects to Google Cloud's Vertex AI to perform Retrieval-Augmented Generation. It queries a specified document corpus to find information relevant to the user's query, which is crucial for providing accurate and context-specific repair solutions.

---
