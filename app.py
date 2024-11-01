# app.py
from flask import Flask, render_template, request, redirect, session, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import pdb
import json
from flask_httpauth import HTTPBasicAuth
from config import Config  # Import the Config class
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')  
auth = HTTPBasicAuth()
app.config.from_object(Config)  # Load the configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoicing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set a secret key for session management
app.secret_key = app.config['SECRET_KEY']  # Replace with a strong secret key

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Custom filter to format numbers with a space as a thousand separator
@app.template_filter('thousands_separator')
def thousands_separator(value):
    """Format a number with a space as a thousand separator."""
    if isinstance(value, (int, float)):
        return f"{value:,.0f}".replace(',', ' ')
    return value

# Load persona information
try:
    with open('personas.json', encoding='utf-8') as f:
        PERSONAS = json.load(f)
except json.JSONDecodeError as e:
    logging.error(f"Error loading personas.json: {e}")
    PERSONAS = {}

# Load translations
try:
    with open('translations.json', encoding='utf-8') as f:
        LANGUAGES = json.load(f)
except json.JSONDecodeError as e:
    logging.error(f"Error loading translations.json: {e}")
    LANGUAGES = {}

# Define the authentication logic
@auth.verify_password
def verify_password(username, password):
    if username == app.config['USERNAME'] and password == app.config['PASSWORD']:
        return True
    return False

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
    discount = db.Column(db.Float, default=0)  # Add discount field
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
@auth.login_required
def index():
    clients = Client.query.all()
    invoices = Invoice.query.all()  # Fetch all invoices
    response = make_response(render_template('index.html', clients=clients, invoices=invoices, PERSONAS=PERSONAS, LANGUAGES=LANGUAGES))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

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
    
    return render_template('add_client.html', client=None, client_id=None)

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
    
    return render_template('add_client.html', client=client, client_id=client_id)

@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    if request.method == 'POST':
        # Retrieve form data
        invoice_id = request.form.get('invoice_id')
        invoice_number = request.form.get('invoice_number')
        invoice_date_str = request.form.get('invoice_date')
        client_id = request.form.get('client_id')
        state = request.form.get('state')
        discount = float(request.form.get('discount', 0))
        apply_vat = request.form.get('apply_vat') == 'on'
        vat_percentage = float(request.form.get('vat_percentage', 0))  # Get VAT percentage from form
        currency = request.form.get('currency')

        # Check for required fields
        if not invoice_id or not invoice_number or not invoice_date_str or not client_id or not state:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('add_invoice'))

        # Convert date string to date object
        try:
            invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()
        except ValueError:
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

        # Calculate discount amount
        discount_amount = subtotal * (discount / 100)

        # Calculate total after discount
        total_after_discount = subtotal - discount_amount

        # Calculate VAT amount if applicable
        vat_amount = 0
        if apply_vat:
            vat_amount = total_after_discount * (vat_percentage / 100)

        # Final total
        total = total_after_discount + vat_amount

        # Create a new invoice
        new_invoice = Invoice(
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            client_id=client_id,
            total=total,
            state=state,
            apply_vat=apply_vat,
            vat_percentage=vat_percentage, 
            currency=currency,
            discount=discount 
        )
        db.session.add(new_invoice)
        db.session.commit()

        # Now that the invoice ID is available, set it for each service
        for service in services:
            service.invoice_id = new_invoice.id  # Set the invoice_id for each service
            db.session.add(service)

        db.session.commit()
        flash("Invoice added successfully!", "success")
        return redirect(url_for('index'))

    # For adding a new invoice, generate a unique invoice ID
    invoice_id = datetime.now().strftime("%Y%m%d%H%M%S")
    clients = Client.query.all()
    vat_percentage = 0  
    return render_template('add_invoice.html', clients=clients, invoice=None, vat_percentage=vat_percentage, invoice_id=invoice_id)

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

        # Fetch the invoice and associated client
        invoice = Invoice.query.get_or_404(invoice_id)
        services = InvoiceService.query.filter_by(invoice_id=invoice.id).all()
        
        # Fetch the client associated with the invoice
        client = Client.query.get(invoice.client_id)  # Assuming invoice has a client_id field

        # Calculate subtotal and total
        subtotal = sum(service.line_total for service in services)
        discount = invoice.discount  # Use the discount from the invoice
        discount_amount = subtotal * (discount / 100)  # Calculate discount amount
        total_after_discount = subtotal - discount_amount  # Total after discount

        # Check if VAT is applied
        apply_vat = invoice.apply_vat
        vat_percentage = invoice.vat_percentage
        vat_amount = 0

        if apply_vat:
            vat_amount = total_after_discount * (vat_percentage / 100)  # Calculate VAT amount
        total = total_after_discount + vat_amount  # Final total

        # Pass all necessary data to the template
        return render_template('print_invoice.html', 
                               invoice=invoice, 
                               services=services, 
                               subtotal=subtotal, 
                               discount=discount, 
                               discount_amount=discount_amount,  # Pass discount amount
                               vat_amount=vat_amount,  # Pass VAT amount
                               total=total, 
                               language_dict=language_dict, 
                               persona_info=persona_info,
                               client=client,  # Pass the client information to the template
                               client_payment_terms=client.payment_terms,  # Pass payment terms to the template
                               PERSONAS=PERSONAS)  # Include PERSONAS here

    elif request.method == 'POST':
        # Handle POST request logic here if needed
        # For example, you might want to handle printing or saving the invoice
        # You can also redirect or render a different template if necessary
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


@app.route('/edit_invoice/<int:invoice_id>', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)  # Fetch the invoice by ID
    logging.debug(f"fetched Invoice ID: {invoice_id}")
    invoice = Invoice.query.get_or_404(invoice_id)
    if request.method == 'GET':
        clients = Client.query.all()
        return render_template('add_invoice.html', clients=clients, invoice=invoice, invoice_id=invoice.invoice_id)
    if request.method == 'POST':
        # Handle form submission
        invoice_number = request.form.get('invoice_number')
        invoice_date_str = request.form.get('invoice_date')
        client_id = request.form.get('client_id')
        state = request.form.get('state')
        discount = float(request.form.get('discount', 0))
        apply_vat = request.form.get('apply_vat') == 'on'
        vat_percentage = float(request.form.get('vat_percentage', 0))
        currency = request.form.get('currency')  # Get currency

        # Update invoice fields
        invoice.invoice_number = invoice_number
        invoice.invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()
        invoice.client_id = client_id
        invoice.state = state
        invoice.discount = discount
        invoice.apply_vat = apply_vat
        invoice.vat_percentage = vat_percentage
        invoice.currency = currency

        # Clear existing services and add updated ones
        InvoiceService.query.filter_by(invoice_id=invoice.id).delete()  # Clear existing services
        line_count = int(request.form.get('line_count', 0))
        for i in range(line_count):
            service = request.form.get(f'service_{i}')
            unit_cost = request.form.get(f'unit_cost_{i}')
            quantity = request.form.get(f'quantity_{i}')

            # Create a new service entry
            new_service = InvoiceService(
                invoice_id=invoice.id,
                service=service,
                unit_cost=float(unit_cost),
                quantity=int(quantity),
                line_total=float(unit_cost) * int(quantity)
            )
            db.session.add(new_service)

        db.session.commit()  # Commit changes to the database
        flash("Invoice updated successfully!", "success")
        return redirect(url_for('index'))

    # For editing an existing invoice, pass the invoice data to the template
    clients = Client.query.all()  # Fetch all clients for the dropdown
    return render_template('add_invoice.html', clients=clients, invoice=invoice)





if __name__ == '__main__':
    app.run(debug=True)





