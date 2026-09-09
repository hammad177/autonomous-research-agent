from langchain_text_splitters import RecursiveCharacterTextSplitter

from autonomous_research_agent.common.constants import CHUNK_SIZE, CHUNK_OVERLAP


class TextChunker:
    def __init__(
        self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        return self.splitter.split_text(text)
