from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from data.db_models import Chunk


class ChunkRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def delete_by_document_id(
        self,
        document_id: UUID,
    ) -> None:

        statement = delete(Chunk).where(
            Chunk.document_id == document_id
        )

        self.db.execute(statement)

    def create_many(
        self,
        chunks: list[Chunk],
    ) -> None:

        self.db.add_all(chunks)

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> list[Chunk]:

        statement = (
            select(Chunk)
            .where(
                Chunk.document_id == document_id
            )
            .order_by(Chunk.chunk_index)
        )

        return list(
            self.db.scalars(statement).all()
        )