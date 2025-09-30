from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

db = SQLAlchemy(model_class=Base)

class Author(db.Model):
    """Model representing an author.

    Attributes:
        id (int): Primary key, auto-incremented identifier for the author.
        name (str): Name of the author.
        birth_date (str): Birth date of the author.
        death_date (str): Death date of the author (optional).
        books (relationship): Collection of books written by the author.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.String, nullable=False)
    death_date = db.Column(db.String)
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        """Return a string representation of the author for debugging."""
        return f"Author(id={self.id}, name={self.name})"

    def __str__(self):
        """Return a human-readable string representation of the author."""
        death = self.death_date if self.death_date else ""
        if death:
            return f"{self.id}. {self.name} ({self.birth_date} - {death})"
        else:
            return f"{self.id}. {self.name} ({self.birth_date})"

class Book(db.Model):
    """Model representing a book.

    Attributes:
        id (int): Primary key, auto-incremented identifier for the book.
        author_id (int): Foreign key linking to the author of the book.
        title (str): Title of the book.
        publication_year (str): Year of publication of the book (optional).
        isbn (int): ISBN number of the book.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.String)
    isbn = db.Column(db.Integer)

    def __repr__(self):
        """Return a string representation of the book for debugging."""
        return f"Book(id={self.id}, title={self.title})"

    def __str__(self):
        """Return a human-readable string representation of the book."""
        pub_year = self.publication_year if self.publication_year else ""
        if pub_year:
            return f"{self.id}. {self.title} ({pub_year})"
        else:
            return f"{self.id}. {self.title}"
