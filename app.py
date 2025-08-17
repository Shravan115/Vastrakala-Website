from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vastrakala.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    stock = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(20), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def welcome():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'category': p.category,
        'image_url': p.image_url,
        'stock': p.stock,
        'badge': p.badge
    } for p in products])

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
    else:
        session['cart'][str(product_id)] = quantity
    
    session.modified = True
    return jsonify({'success': True, 'cart_count': len(session['cart'])})

@app.route('/api/cart')
def get_cart():
    if 'cart' not in session:
        return jsonify({'items': [], 'total': 0})
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'total': item_total,
                'image_url': product.image_url
            })
            total += item_total
    
    return jsonify({'items': cart_items, 'total': total})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            login_user(user)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email already registered'})
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    
    # Create order
    order = Order(user_id=current_user.id, total_amount=data['total'])
    db.session.add(order)
    db.session.flush()
    
    # Add order items
    for item in data['items']:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
    
    # Clear cart
    session.pop('cart', None)
    
    db.session.commit()
    
    return jsonify({'success': True, 'order_id': order.id})

# Admin routes
@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=data['category'],
        image_url=data['image_url'],
        stock=int(data['stock']),
        badge=data.get('badge', '')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({'success': True, 'product_id': product.id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample products if database is empty
        if not Product.query.first():
            sample_products = [
                {
                    'name': 'Handloom Saree',
                    'description': 'Elegant, handwoven saree with traditional motifs. Available in multiple colors and patterns.',
                    'price': 2499.0,
                    'category': 'Saree',
                    'image_url': 'https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcQWGJkt-ll5GyIDZ1YRjgD3MXIrYcxDy_mUTvezl3M-fkea_KFdlVGU7b-iEu5ZrsyiXH3a0K1Swz6l0zfCxwaVlxDtWBWujvMFP9cxALIY',
                    'stock': 10,
                    'badge': 'Best Seller'
                },
                {
                    'name': 'Men\'s Kurta',
                    'description': 'Classic cotton kurta for festive occasions. Breathable fabric, available in all sizes.',
                    'price': 1299.0,
                    'category': 'Kurta',
                    'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTStgxh9rbG0qTu55w82ZkRARnUvVhKQ3Ii0w&s',
                    'stock': 15,
                    'badge': 'New'
                }
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()
    
    app.run(debug=True) 