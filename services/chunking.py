from dataclasses import dataclass


@dataclass
class ChunkResult:
    index: int
    text: str
    start_offset: int
    end_offset: int


class FixedSizeChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if overlap < 0:
            raise ValueError(
                "overlap cannot be negative"
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[ChunkResult]:

        if not text:
            return []

        chunks: list[ChunkResult] = []

        step = self.chunk_size - self.overlap

        index = 0
        start = 0

        while start < len(text):

            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunks.append(
                ChunkResult(
                    index=index,
                    text=text[start:end],
                    start_offset=start,
                    end_offset=end,
                )
            )
            if end == len(text):
                break

            start += step
            index += 1

        return chunks