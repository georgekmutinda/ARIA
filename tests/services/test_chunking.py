from services.chunking import FixedSizeChunker


def test_fixed_size_chunking():

    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunker = FixedSizeChunker(
        chunk_size=10,
        overlap=2,
    )

    chunks = chunker.chunk(text)

    assert chunks[0].text == "ABCDEFGHIJ"
    assert chunks[1].text == "IJKLMNOPQR"
    assert chunks[2].text == "QRSTUVWXYZ"

    assert chunks[0].start_offset == 0
    assert chunks[0].end_offset == 10

    assert chunks[1].start_offset == 8
    assert chunks[1].end_offset == 18

    assert chunks[2].start_offset == 16
    assert chunks[2].end_offset == 26