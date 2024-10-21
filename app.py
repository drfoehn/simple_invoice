# app.py
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import pdb

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoicing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

db = SQLAlchemy(app)

# Define the Client model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=True)
    vat_number = db.Column(db.String(50), nullable=True)  # VAT identification number
    vat_percentage = db.Column(db.Float, nullable=True)  # VAT percentage
    street = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    currency = db.Column(db.String(10), nullable=True)  # Currency field
    language = db.Column(db.String(10), nullable=True)
    payment_terms = db.Column(db.String(300), nullable=True)
    invoices = db.relationship('Invoice', backref='client', lazy=True)

# Define the Invoice model
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    invoice_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique invoice ID
    invoice_number = db.Column(db.String(50), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    state = db.Column(db.String(20), nullable=False)
    apply_vat = db.Column(db.Boolean, default=False)
    vat_percentage = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True)  # Currency field
    services = db.relationship('InvoiceService', backref='invoice', lazy=True, cascade="all, delete-orphan")

class InvoiceService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    service = db.Column(db.String(100), nullable=True)
    unit_cost = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    line_total = db.Column(db.Float, nullable=True)

# Create the database and tables
with app.app_context():
    db.create_all()



# Define the routes
@app.route('/')
def index():

    clients = Client.query.all()
    invoices = Invoice.query.all()  # Fetch all invoices
    return render_template('index.html', clients=clients, invoices=invoices, PERSONAS=PERSONAS)  # Pass PERSONAS here


@app.route('/create_client', methods=['POST', 'GET'])
def create_client():
    #pdb.set_trace()  # Set a breakpoint here
    if request.method == 'POST':
        company_name = request.form['company_name']
        vat_number = request.form['vat_number']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        country = request.form['country']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        currency = request.form['currency']
        language = request.form['language']
        payment_terms = request.form['payment_terms']
        
        new_client = Client(
            company_name=company_name,
            vat_number=vat_number,
            street=street,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            currency=currency,
            language=language,
            payment_terms=payment_terms
        )
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('edit_client.html', client=None, client_id=None)

@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    logging.debug(f"Editing client: {client_id}")  # Debugging line
    if request.method == 'POST':
        # Update the client with the correct field names
        client.company_name = request.form['company_name']
        client.vat_number = request.form['vat_number']
        client.vat_percentage = request.form['vat_percentage']  # Ensure this is included
        client.street = request.form['street']
        client.city = request.form['city']
        client.state = request.form['state']
        client.postal_code = request.form['postal_code']
        client.country = request.form['country']
        client.first_name = request.form['first_name']
        client.last_name = request.form['last_name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        client.currency = request.form['currency']
        client.language = request.form['language']
        client.payment_terms = request.form['payment_terms']
        
        db.session.commit()
        logging.debug("Client updated successfully.")  # Debugging line
        return redirect(url_for('index'))
    
    return render_template('edit_client.html', client=client, client_id=client_id)

@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    #pdb.set_trace()  # Set a breakpoint here
    if request.method == 'POST':
        # Handle form submission
        invoice_id = request.form.get('invoice_id')  # Get the generated invoice ID
        invoice_number = request.form.get('invoice_number')
        invoice_date_str = request.form.get('invoice_date')
        client_id = request.form.get('client_id')
        state = request.form.get('state')
        discount = float(request.form.get('discount', 0))
        apply_vat = request.form.get('apply_vat') == 'on'
        vat_percentage = float(request.form.get('vat_percentage', 0))
        currency = request.form.get('currency')  # Get currency

        # Check for required fields
        if not invoice_id or not invoice_number or not invoice_date_str or not client_id or not state:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('add_invoice'))

        # Convert date string to date object
        try:
            invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()
        except ValueError:
            logging.error("Invalid date format.")
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for('add_invoice'))

        # Initialize subtotal
        subtotal = 0
        services = []  # List to hold service entries

        # Collect services
        line_count = int(request.form.get('line_count', 0))
        for i in range(line_count):
            service = request.form.get(f'service_{i}')
            unit_cost = request.form.get(f'unit_cost_{i}')
            quantity = request.form.get(f'quantity_{i}')

            # Check for service details
            if not service or not unit_cost or not quantity:
                flash("Please fill in all service details.", "error")
                return redirect(url_for('add_invoice'))

            try:
                unit_cost = float(unit_cost)
                quantity = int(quantity)
            except ValueError:
                flash("Invalid unit cost or quantity. Please enter valid numbers.", "error")
                return redirect(url_for('add_invoice'))

            line_total = unit_cost * quantity
            subtotal += line_total  # Accumulate subtotal

            # Create a service entry to be added later
            services.append(InvoiceService(service=service, unit_cost=unit_cost, quantity=quantity, line_total=line_total))

        # Calculate total after adding all services
        total = subtotal - (subtotal * (discount / 100))

        # Apply VAT if selected
        if apply_vat:
            vat_amount = total * (vat_percentage / 100)
            total += vat_amount  # Add VAT to total

        # Create the invoice with the calculated total and invoice_id
        new_invoice = Invoice(
            id=invoice_id,
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            client_id=client_id,
            total=total,
            state=state,
            apply_vat=apply_vat,
            vat_percentage=vat_percentage,
            currency=currency  # Set the currency
        )

        # Add the invoice and services to the session
        db.session.add(new_invoice)
        db.session.commit()  # Commit to save the invoice and get its ID

        # Now that the invoice ID is available, set it for each service
        for service in services:
            service.invoice_id = new_invoice.id  # Set the invoice_id for each service
            db.session.add(service)

        # Commit all changes to the database
        db.session.commit()

        flash("Invoice added successfully!", "success")
        return redirect(url_for('index'))

    # Generate a unique invoice ID using the current date and time
    invoice_id = datetime.now().strftime("%Y%m%d%H%M%S")  # Format: YYYYMMDDHHMMSS
    clients = Client.query.all()
    
    # Set default VAT percentage to 0 initially
    vat_percentage = 0  

    # If a client is selected, fetch the VAT percentage
    if request.args.get('client_id'):
        selected_client = Client.query.get(request.args.get('client_id'))
        if selected_client:
            vat_percentage = selected_client.vat_percentage  # Get the VAT percentage from the selected client
            logging.debug(f"VAT Percentage for client {selected_client.id}: {vat_percentage}")

    return render_template('add_invoice.html', clients=clients, invoice_id=invoice_id, vat_percentage=vat_percentage)

@app.route('/client_invoices/<int:client_id>')
def client_invoices(client_id):
    client = Client.query.get_or_404(client_id)
    client_invoices = Invoice.query.filter_by(client_id=client_id).all()
    return render_template('client_invoices.html', client=client, client_invoices=client_invoices)

@app.route('/print_invoice/<int:invoice_id>', methods=['GET', 'POST'])
def print_invoice(invoice_id):
    if request.method == 'GET':
        # Get the selected language from the query parameters
        selected_language = request.args.get('language', 'en')  # Default to English if not provided
        selected_persona = request.args.get('persona', 'persona1')  # Default to the first persona

        language_dict = LANGUAGES.get(selected_language, LANGUAGES['en'])  # Fallback to English
        persona_info = PERSONAS.get(selected_persona, PERSONAS['persona1'])  # Get persona info

        # Debugging: Print the selected language and dictionary
        print(f"Selected Language: {selected_language}")
        print(f"Selected Persona: {selected_persona}")
        print(f"Persona Info: {persona_info}")

        invoice = Invoice.query.get_or_404(invoice_id)
        services = InvoiceService.query.filter_by(invoice_id=invoice.id).all()
        
        # Fetch the client associated with the invoice
        client = Client.query.get(invoice.client_id)  # Assuming invoice has a client_id field

        # Calculate subtotal and total
        subtotal = sum(service.line_total for service in services)
        discount = 0  # You can modify this if you want to include discount logic
        total = subtotal - (subtotal * (discount / 100))

        # Check if VAT is applied
        apply_vat = invoice.apply_vat
        vat_percentage = invoice.vat_percentage
        vat_amount = 0

        if apply_vat:
            vat_amount = total * (vat_percentage / 100)
            total += vat_amount  # Add VAT to total

        # Pass PERSONAS to the template
        return render_template('print_invoice.html', 
                               invoice=invoice, 
                               services=services, 
                               subtotal=subtotal, 
                               discount=discount, 
                               vat_amount=vat_amount, 
                               total=total, 
                               language_dict=language_dict, 
                               persona_info=persona_info,
                               client_payment_terms=client.payment_terms,  # Pass payment terms to the template
                               PERSONAS=PERSONAS)  # Include PERSONAS here

    elif request.method == 'POST':
        return redirect(url_for('index'))  # Redirect to the index page or another appropriate action

@app.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash("Client deleted successfully!", "success")
    return redirect(url_for('clients'))  # Redirect to the clients page

# Define the route for clients
@app.route('/clients')
def clients():
    clients = Client.query.all()  # Fetch all clients from the database
    return render_template('clients.html', clients=clients)  # Render the clients template

@app.route('/delete_invoice/<int:invoice_id>', methods=['POST'])
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    flash("Invoice deleted successfully!", "success")
    return redirect(url_for('index'))  # Redirect back to the invoices list

# Language dictionaries
LANGUAGES = {
    'en': {
        'invoice': 'Invoice',
        'date': 'Date',
        'client': 'Client',
        'currency': 'Currency',
        'services': 'Services',
        'service': 'Service',
        'unit_cost': 'Unit Cost',
        'quantity': 'Quantity',
        'line_total': 'Line Total',
        'summary': 'Summary',
        'subtotal': 'Subtotal',
        'discount': 'Discount',
        'vat': 'VAT',
        'total': 'Total',
        'subtotal': 'Subtotal:',
        'vat_amount': 'VAT Amount:',
        'final_total': 'Final Total:',
        'client_name': 'Client Name:',
        'invoice_date': 'Invoice Date:',
    },
    'fr': {
        'invoice': 'Facture',
        'date': 'Date',
        'client': 'Client',
        'currency': 'Devise',
        'services': 'Services',
        'service': 'Service',
        'unit_cost': 'Coût Unitaire',
        'quantity': 'Quantité',
        'line_total': 'Total de la Ligne',
        'summary': 'Résumé',
        'subtotal': 'Sous-total',
        'discount': 'Remise',
        'vat': 'TVA',
        'total': 'Total'
    },
    'de': {
        'invoice': 'Rechnung',
        'date': 'Datum',
        'client': 'Kunde',
        'currency': 'Währung',
        'services': 'Dienstleistungen',
        'service': 'Dienstleistung',
        'unit_cost': 'Einzelpreis',
        'quantity': 'Menge',
        'line_total': 'Gesamtbetrag',
        'summary': 'Zusammenfassung',
        'subtotal': 'Zwischensumme',
        'discount': 'Rabatt',
        'vat': 'USt',
        'total': 'Gesamt'
    }
}

# Define personas
PERSONAS = {
    'persona1': {
        'prefix': 'Mr.',
        'first_name': 'John',
        'last_name': 'Doe',
        'suffix': 'Jr.',
        'address': {
            'street': '123 Main St',
            'city': 'Anytown',
            'postal_code': '12345',
            'state': 'CA',
            'country': 'USA'
        },
        'tel': '123-456-7890',
        'email': 'john.doe@example.com',
        'vat_number': 'US123456789',
        'bank_info': {
            'bank_name': 'Bank of America',
            'iban': 'US12345678901234567890',
            'bic': 'BOFAUS3N'
        }
    },
    'persona2': {
        'prefix': 'Ms.',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'suffix': '',
        'address': {
            'street': '456 Elm St',
            'city': 'Othertown',
            'postal_code': '67890',
            'state': 'NY',
            'country': 'USA'
        },
        'tel': '987-654-3210',
        'email': 'jane.smith@example.com',
        'vat_number': 'US987654321',
        'bank_info': {
            'bank_name': 'Chase Bank',
            'iban': 'US09876543210987654321',
            'bic': 'CHASUS33'
        }
    }
    # Add more personas as needed
}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
