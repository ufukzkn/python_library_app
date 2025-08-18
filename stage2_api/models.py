from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    isbn: str  # benzersiz kimlik
    is_borrowed: bool = False  # Stage 1'de şart değil ama dursun (ileriye dönük)

    def __str__(self) -> str:
        # "Ulysses by James Joyce (ISBN: 978-0199535675)" formatı
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

    def borrow_book(self) -> None:
        if self.is_borrowed:
            raise ValueError(f"'{self.title}' is already borrowed.")
        self.is_borrowed = True

    def return_book(self) -> None:
        if not self.is_borrowed:
            raise ValueError(f"'{self.title}' was not borrowed.")
        self.is_borrowed = False
