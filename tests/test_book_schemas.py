from src.library_catalog.api.v1.schemas.book import BookCreate, BookUpdate


def test_isbn_is_normalized_for_create_and_update() -> None:
    create = BookCreate(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        isbn="978-0-13-235088-4",
    )
    update = BookUpdate(isbn="978 0 13 235088 4")

    assert create.isbn == "9780132350884"
    assert update.isbn == "9780132350884"
