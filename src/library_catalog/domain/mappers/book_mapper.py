from ...api.v1.schemas.book import ShowBook
from ...data.models.book import Book


class BookMapper:
    @staticmethod
    def to_show_book(book: Book) -> ShowBook:
        return ShowBook(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            year=book.year,
            genre=book.genre,
            pages=book.pages,
            description=book.description,
            available=book.available,
            created_at=book.created_at,
            updated_at=book.updated_at,
            isbn=book.isbn,
            extra=book.extra,
        )

    @staticmethod
    def to_show_books(books: list[Book]) -> list[ShowBook]:
        return list(map(BookMapper.to_show_book, books))
