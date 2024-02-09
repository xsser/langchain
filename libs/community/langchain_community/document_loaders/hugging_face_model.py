import requests
from typing import Iterator, List, Optional

from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader

class HuggingFaceModelLoader(BaseLoader):
    """Load model information from `Hugging Face Hub`, including README content."""

    BASE_URL = "https://huggingface.co/api/models"
    README_BASE_URL = "https://huggingface.co/{model_id}/raw/main/README.md"

    def __init__(
        self,
        search: Optional[str] = None,
        author: Optional[str] = None,
        filter: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        limit: Optional[int] = 3,
        full: Optional[bool] = None,
        config: Optional[bool] = None,
    ):
        """Initialize the HuggingFaceModelLoader.

        Args:
            search: Filter based on substrings for repos and their usernames.
            author: Filter models by an author or organization.
            filter: Filter based on tags.
            sort: Property to use when sorting.
            direction: Direction in which to sort.
            limit: Limit the number of models fetched.
            full: Whether to fetch most model data.
            config: Whether to also fetch the repo config.
        """

        self.params = {
            "search": search,
            "author": author,
            "filter": filter,
            "sort": sort,
            "direction": direction,
            "limit": limit,
            "full": full,
            "config": config,
        }

    def fetch_models(self) -> List[dict]:
        """Fetch model information from Hugging Face Hub."""
        response = requests.get(self.BASE_URL, params={k: v for k, v in self.params.items() if v is not None})
        response.raise_for_status()
        return response.json()

    def fetch_readme_content(self, model_id: str) -> str:
        """Fetch the README content for a given model."""
        readme_url = self.README_BASE_URL.format(model_id=model_id)
        try:
            response = requests.get(readme_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return "README not available for this model."

    def lazy_load(self) -> Iterator[Document]:
        """Load model information lazily, including README content."""
        models = self.fetch_models()

        for model in models:
            model_id = model.get("modelId", "")
            readme_content = self.fetch_readme_content(model_id)
            
            yield Document(
                page_content=readme_content,
                metadata=model,
            )

    def load(self) -> List[Document]:
        """Load model information, including README content."""
        return list(self.lazy_load())



if __name__ == "__main__":
    loader = HuggingFaceModelLoader(search="phi-2", sort="downloads", direction=-1 ,limit=10)
    documents = loader.load()
    # pretty print the first document with all json fields expanded so that we can see the structure
    import json
    print(len(documents))
    print(json.dumps(documents[0].metadata, indent=4))
    print(documents[0].page_content)
    #print(documents)