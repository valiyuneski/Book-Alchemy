import os
from flask import Flask, render_template, request, redirect, url_for
from data_models import db, Author, Book
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configure the database URI and tracking modifications
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "data", "library.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Only run this block once to create the database tables.
with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("book"):  # replace with your table name
        print("Creating tables...")
        db.create_all()
        print("Tables created.")
    else:
        print("Tables already exist. Skipping.")


@app.route('/', methods=['GET'])
def home():
    """Render the home page with a list of books."""
    # Retrieves books from the database, allowing for sorting and searching.
    # Renders HTML page of the home view with books.
    
    sort_by = request.args.get('sort_by', 'no_sort')
    search = request.args.get('search')

    # Search
    if search:
        books = Book.query.filter(Book.title.like(f'%{search}%')).order_by(Book.title).all()
        return render_template('home.html', books=books, success=bool(books))

    # Sorting
    if sort_by == 'title':
        books = Book.query.order_by(Book.title).all()
    elif sort_by == 'author':
        books = Book.query.join(Author).order_by(Author.name).all()
    elif sort_by == 'publication_year':
        books = Book.query.order_by(Book.publication_year).all()
    elif sort_by == 'no_sort':
        books = Book.query.all()
    else:
        books = Book.query.all()  # Default case if no valid sort_by

    return render_template('home.html', books=books, success=True)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Add a new author to the database."""
    # Handles both GET and POST requests. On a POST request, it retrieves
    # author details from the form and adds the author to the database.

    # Redirects to the same page with a success flag if the author is added.
    # Renders the add author form on a GET request.
    if request.method == 'POST':
        author_name = request.form.get('name').strip() # type: ignore
        birth_date_str = request.form.get('birth_date').strip() # type: ignore
        death_date_str = request.form.get('death_date').strip() # type: ignore

        # Always required
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()

        # Only parse if provided
        death_date = None
        if death_date_str:
            death_date = datetime.strptime(death_date_str, "%Y-%m-%d").date()

        author = Author(name=author_name, birth_date=birth_date, death_date=death_date)
        try:
            db.session.add(author)
            db.session.commit()
            return redirect(url_for('add_author', success=True), 302)
        except SQLAlchemyError as e:
            db.session.rollback()
            return render_template(
                'add_author.html',
                error=f"Database error: {str(e)}"
            )

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """ Add a new book to the database. """
    # Handles both GET and POST requests. On a POST request, it retrieves
    # book details from the form and adds the book to the database.

    # Redirects to the same page with a success flag if the book is added.
    # Renders the add book form along with a list of authors on a GET request.

    if request.method == 'POST':
        title = request.form.get('title').strip() # type: ignore
        author_id = int(request.form.get('author_id').strip()) # type: ignore
        publication_year_str = request.form.get('publication_year').strip() # type: ignore
        isbn = request.form.get('isbn').strip() # type: ignore

        # Extract year safely
        publication_year = None
        if publication_year_str:
            # Handle both "YYYY" and accidental "YYYY-MM-DD"
            try:
                if "-" in publication_year_str:
                    publication_year = int(publication_year_str.split("-")[0])  # take first part
                else:
                    publication_year = int(publication_year_str)
            except ValueError:
                return render_template(
                    'add_book.html',
                    authors=Author.query.all(),
                    error=f"Invalid year format: {publication_year_str}"
                )

        # Check for duplicate ISBN
        existing = Book.query.filter_by(isbn=isbn).first()
        if existing:
            return render_template(
                'add_book.html',
                authors=Author.query.all(),
                error=f"A book with ISBN {isbn} already exists."
            )

        book = Book(
            title=title,
            author_id=author_id,
            publication_year=publication_year,
            isbn=isbn
        )
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('add_book', success=True), 302)

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """ Deletes a book identified by the book_id parameter. """
    #Redirects to the home page after the book is deleted.

    book = Book.query.get(book_id)

    if not book:
        # Book not found
        return redirect(url_for('home', error="Book not found"), 302)

    try:
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('home', success_delete=True), 302)
    except SQLAlchemyError as e:
        db.session.rollback()
        return redirect(url_for('home', error=f"Error deleting book: {str(e)}"), 302)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
