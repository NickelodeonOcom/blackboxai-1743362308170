from flask import Flask, render_template, request, jsonify, session
import g4f
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Sample product data
products = {
    "blades": [
        {"id": 1, "name": "Pro Blade X", "price": 89.99, "image": "blade1.jpg"},
        {"id": 2, "name": "Carbon Fiber Blade", "price": 129.99, "image": "blade2.jpg"}
    ],
    "rubbers": [
        {"id": 3, "name": "Spin Master", "price": 49.99, "image": "rubber1.jpg"},
        {"id": 4, "name": "Speed Demon", "price": 59.99, "image": "rubber2.jpg"}
    ],
    "paddles": [
        {"id": 5, "name": "Beginner Paddle", "price": 39.99, "image": "paddle1.jpg"},
        {"id": 6, "name": "Pro Tournament Paddle", "price": 149.99, "image": "paddle2.jpg"}
    ],
    "balls": [
        {"id": 7, "name": "Training Balls (6-pack)", "price": 9.99, "image": "balls1.jpg"},
        {"id": 8, "name": "Tournament Balls (3-pack)", "price": 12.99, "image": "balls2.jpg"}
    ]
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def product_list():
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Find product in all categories
    for category in products.values():
        for product in category:
            if product['id'] == product_id:
                return render_template('product-detail.html', product=product)
    return "Product not found", 404

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)

@app.route('/ai-adviser')
def ai_adviser():
    return render_template('ai-adviser.html')

@app.route('/api/ai', methods=['POST'])
def ai_response():
    try:
        user_query = request.json['query']
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": f"Act as a ping pong equipment expert. {user_query}"}]
        )
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    if 'cart' not in session:
        session['cart'] = []
        
    # Check if product already in cart
    for item in session['cart']:
        if item['id'] == product_id:
            item['quantity'] += quantity
            session.modified = True
            return jsonify({"success": True})
    
    # Find product to add
    for category in products.values():
        for product in category:
            if product['id'] == product_id:
                session['cart'].append({
                    **product,
                    'quantity': quantity
                })
                session.modified = True
                return jsonify({"success": True})
    
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/update-cart', methods=['POST'])
def update_cart():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    if 'cart' not in session:
        return jsonify({"error": "Cart not found"}), 404
        
    for item in session['cart']:
        if item['id'] == product_id:
            item['quantity'] = quantity
            session.modified = True
            return jsonify({"success": True})
    
    return jsonify({"error": "Product not in cart"}), 404

@app.route('/api/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = request.json.get('product_id')
    
    if 'cart' not in session:
        return jsonify({"error": "Cart not found"}), 404
        
    session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
    session.modified = True
    return jsonify({"success": True})

@app.route('/api/cart-count')
def cart_count():
    count = sum(item['quantity'] for item in session.get('cart', []))
    return jsonify({"count": count})

if __name__ == '__main__':
    app.run(debug=True)