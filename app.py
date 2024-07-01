from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import hashlib
import os
from werkzeug.utils import secure_filename
import base64
import smtplib
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL Connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Arth@F1',
    database='visionscripts'
)
cursor = db.cursor()

# Routes
@app.route('/')
def index():
    role=session.get('role',None)
    username = session.get('username', None)
    return render_template('index.html', username=username,role=role)

@app.route('/marketing')
def marketing():
    role=session.get('role',None)
    username = session.get('username', None)
    cursor.execute("SELECT * FROM products where visibility='on'")
    products = cursor.fetchall()
    return render_template('marketing.html', products=products,username=username,role=role)
@app.route('/websitedev')
def websitedev():
    role=session.get('role',None)
    username = session.get('username', None)
    cursor.execute("SELECT * FROM webservs where visibility='on'")
    webserv = cursor.fetchall()
    return render_template('website-dev.html', webserv=webserv,username=username,role=role)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        try:
            cursor.execute('INSERT INTO contact_inquiries (name, email, message) VALUES (%s, %s, %s)',
                           (name, email, message))
            db.commit()
            flash('Your inquiry has been submitted successfully. We will get back to you soon!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error submitting inquiry: {err}', 'danger')

    return render_template('contact.html')

@app.route('/admin')
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/about')
def about():
    role=session.get('role',None)
    
    username = session.get('username', None)
    return render_template('about.html',username=username,role=role)

@app.route('/product_admin')
def product_admin():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('product_admin.html', products=products)

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    db.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('product_admin'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        cost_price = request.form['cost_price']
        selling_price = request.form['selling_price']
        discount = request.form['discount']
        stock = request.form['stock']
        visibility = request.form['visibility']
        image = request.form['image']

        try:
            cursor.execute('INSERT INTO products (name, description, price, cost_price, selling_price, discount, stock, visibility, image) '
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (name, description, price, cost_price, selling_price, discount, stock, visibility, image))
            db.commit()
            flash('Product added successfully', 'success')
            return redirect(url_for('product_admin'))
        except mysql.connector.Error as err:
            flash(f'Error adding product: {err}', 'danger')

    return render_template('product_admin.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))

    if request.method == 'GET':
        cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
        product = cursor.fetchone()

        if product:
            return render_template('edit_product.html', product=product)
        else:
            flash(f'Product with ID {id} not found', 'danger')
            return redirect(url_for('product_admin'))
    
    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        cost_price = request.form['cost_price']
        selling_price = request.form['selling_price']
        discount = request.form['discount']
        stock = request.form['stock']
        visibility = request.form['visibility']
        image = request.form['image']

        try:
            cursor.execute('UPDATE products SET name=%s, description=%s, price=%s, cost_price=%s, selling_price=%s, discount=%s, stock=%s, visibility=%s, image=%s WHERE id=%s',
                           (name, description, price, cost_price, selling_price, discount, stock, visibility, image, id))
            db.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('product_admin'))
        except mysql.connector.Error as err:
            flash(f'Error updating product: {err}', 'danger')
            return redirect(url_for('edit_product', id=id))

@app.route('/webserv_admin')
def webserv_admin():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))
    cursor.execute('SELECT * FROM webservs')
    webservs = cursor.fetchall()
    return render_template('webserv_admin.html', webservs=webservs)


@app.route('/delete_webserv/<int:id>', methods=['POST'])
def delete_webserv(id):
    cursor.execute('DELETE FROM webservs WHERE id = %s', (id,))
    db.commit()
    flash('webserv deleted successfully', 'success')
    return redirect(url_for('webserv_admin'))


@app.route('/add_webserv', methods=['GET', 'POST'])
def add_webserv():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))


    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        cost_price = request.form['cost_price']
        selling_price = request.form['selling_price']
        discount = request.form['discount']
        
        visibility = request.form['visibility']
        image = request.form['image']


        try:
            cursor.execute('INSERT INTO webservs (name, description, price, cost_price, selling_price, discount, visibility, image) '
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                           (name, description, price, cost_price, selling_price, discount, visibility, image))
            db.commit()
            flash('webserv added successfully', 'success')
            return redirect(url_for('webserv_admin'))
        except mysql.connector.Error as err:
            flash(f'Error adding webserv: {err}', 'danger')


    return render_template('webserv_admin.html')


@app.route('/edit_webserv/<int:id>', methods=['GET', 'POST'])
def edit_webserv(id):
    if 'username' not in session or session.get('role') != 'admin':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('login'))


    if request.method == 'GET':
        cursor.execute('SELECT * FROM webservs WHERE id = %s', (id,))
        webserv = cursor.fetchone()


        if webserv:
            return render_template('edit_webserv.html', webserv=webserv)
        else:
            flash(f'webserv with ID {id} not found', 'danger')
            return redirect(url_for('webserv_admin'))
   
    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        cost_price = request.form['cost_price']
        selling_price = request.form['selling_price']
        discount = request.form['discount']
        
        visibility = request.form['visibility']
        image = request.form['image']


        try:
            cursor.execute('UPDATE webservs SET name=%s, description=%s, price=%s, cost_price=%s, selling_price=%s, discount=%s,  visibility=%s, image=%s WHERE id=%s',
                           (name, description, price, cost_price, selling_price, discount, visibility, image, id))
            db.commit()
            flash('webserv updated successfully', 'success')
            return redirect(url_for('webserv_admin'))
        except mysql.connector.Error as err:
            flash(f'Error updating webserv: {err}', 'danger')
            return redirect(url_for('edit_webserv', id=id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, hashed_password))
        user = cursor.fetchone()

        if user:
            session['username'] = user[1]  # User's name
            session['email'] = user[2]
            session['role'] = user[4]
            flash('Login successful!', 'success')
            if user[4] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        role = request.form['role']

        try:
            cursor.execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)', 
                           (name, email, hashed_password, role))
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists. Please use a different email.', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))
@app.route('/user_management')
def user_management():
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return render_template('user_management.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)', 
                       (name, email, hashed_password, role))
        db.commit()
        flash('User added successfully', 'success')
    except mysql.connector.IntegrityError:
        flash('Email already exists. Please use a different email.', 'danger')

    return redirect(url_for('user_management'))

@app.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute('UPDATE users SET name=%s, email=%s, password=%s, role=%s WHERE id=%s', 
                       (name, email, hashed_password, role, id))
        db.commit()
        flash('User updated successfully', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating user: {err}', 'danger')

    return redirect(url_for('user_management'))

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    cursor.execute('DELETE FROM users WHERE id = %s', (id,))
    db.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('user_management'))
if __name__ == '__main__':
    app.run(debug=True)
