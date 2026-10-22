from pathlib import Path

from pypdf import PdfReader


class ExtractionService:

    def extract(
        self,
        file_path: Path,
        content_type: str,
    ) -> str:

        if content_type == "text/plain":
            return file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

        if content_type == "application/pdf":
            reader = PdfReader(file_path)

            pages: list[str] = []

            for page in reader.pages:
                pages.append(
                    page.extract_text() or ""
                )

            return "\n".join(pages)

        raise ValueError(
            f"Unsupported extraction type: {content_type}"
        )