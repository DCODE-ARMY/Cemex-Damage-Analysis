import base64
from pathlib import Path
from typing import Optional, Type

from crewai.tools import BaseTool
from openai import OpenAI
from pydantic import BaseModel, field_validator, Field

# Schema is updated to use Field for better description, though your original works too.
class VisionToolSchema(BaseModel):
    """Input for Vision Tool."""

    image_path_url: str = Field(..., description="The local path or URL of the image to be analyzed.")
    query: Optional[str] = Field(
        None, 
        description="A specific question to ask about the image. If not provided, a general description will be generated."
    )

    @field_validator("image_path_url")
    def validate_image_path_url(cls, v: str) -> str:
        if v.startswith("http"):
            return v
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Image file does not exist: {v}")
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        if path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Unsupported image format. Supported formats: {valid_extensions}")
        return v


class VisionTool(BaseTool):
    # Name and description are updated for clarity
    name: str = "Vision Analysis Tool"
    description: str = (
        "This tool uses an AI vision model to analyze an image. "
        "It can provide a general description or answer a specific query about the image content."
        "This is only for image analysis and it does not provide any other information or solutions."
    )
    args_schema: Type[BaseModel] = VisionToolSchema
    _client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """Cached OpenAI client instance."""
        if self._client is None:
            self._client = OpenAI()
        return self._client

    # The _run signature is now much cleaner
    def _run(self, image_path_url: str, query: Optional[str] = None) -> str:
        try:
            # The manual validation line is removed, as CrewAI handles it.
            if image_path_url.startswith("http"):
                image_data = image_path_url
            else:
                try:
                    base64_image = self._encode_image(image_path_url)
                    image_data = f"data:image/jpeg;base64,{base64_image}"
                except Exception as e:
                    return f"Error processing image: {str(e)}"
            
            # The prompt logic is simplified using the named 'query' argument
            prompt = query if query else "Describe the contents of this image in detail."
            
            response = self.client.chat.completions.create(
                model="gpt-4o", # Recommended for higher accuracy on complex tasks
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data},
                            },
                        ],
                    }
                ],
                max_tokens=500, # Increased for more detailed responses
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"An error occurred: {str(e)}"

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")