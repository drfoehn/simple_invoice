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

## Customizing Personas and Translations

### Adapting Personas

1. **Locate the `personas.json` file** in the root directory of the project. This file contains the persona information used in the application.

2. **Edit the `personas.json` file** to add or modify personas. The structure of the file is as follows:

   ```json
   {
       "persona1": {
           "prefix": "Mr.",
           "first_name": "John",
           "last_name": "Doe",
           "logo": "img/logo_persona1.png",
           "suffix": "Jr.",
           "address": {
               "street": "123 Main St",
               "city": "Anytown",
               "postal_code": "12345",
               "state": "CA",
               "country": "USA"
           },
           "tel": "123-456-7890",
           "email": "john.doe@example.com",
           "vat_number": "US123456789",
           "bank_info": {
               "account_holder": "John Doe",
               "bank_name": "Bank of America",
               "iban": "US12345678901234567890",
               "bic": "BOFAUS3N"
           }
       },
       ...
   }
   ```

3. **Add new personas** by following the same structure. Ensure that each persona has a unique key (e.g., `persona2`, `persona3`, etc.).

### Adapting Translations

1. **Locate the `translations.json` file** in the root directory of the project. This file contains the translations for different languages used in the application.

2. **Edit the `translations.json` file** to add or modify translations. The structure of the file is as follows:

   ```json
   {
       "en": {
           "invoice": "Invoice",
           "date": "Date",
           ...
       },
       "fr": {
           "invoice": "Facture",
           "date": "Date",
           ...
       },
       ...
   }
   ```

3. **Add new languages** by following the same structure. Ensure that each language has a unique key (e.g., `de` for German, `es` for Spanish, etc.).

4. **Modify existing translations** to fit your needs by changing the text within the quotes.

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
