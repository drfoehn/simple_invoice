# Simple Invoice App

A simple invoicing application built with Flask, SQLAlchemy, and Bootstrap. This app allows users to create, manage, and print invoices for their clients.

## Features

- Create and manage clients
- Create and manage invoices
- Print invoices in a user-friendly format
- Support for multiple languages
- Responsive design using Bootstrap

## Requirements

- Python 3.x
- Flask
- Flask-SQLAlchemy

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/drfoehn/simple_invoice.git
   cd simple_invoice
   ```

2. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

3. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:

   Run the following command to create the database and tables:

   ```bash
   python -c "from app import db; db.create_all()"
   ```

## Usage

1. **Run the application**:

   ```bash
   python app.py
   ```

   The app will be available at `http://127.0.0.1:8080`.

2. **Access the application**: Open your web browser and navigate to `http://127.0.0.1:8080` to start using the invoicing app.

3. **Create clients and invoices**: Use the provided forms to add clients and create invoices.

4. **Print invoices**: You can print invoices directly from the application.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used.
- [SQLAlchemy](https://www.sqlalchemy.org/) - The ORM used for database interactions.
- [Bootstrap](https://getbootstrap.com/) - The CSS framework used for responsive design.