from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory storage for orders
orders = []

@app.route('/')
def index():
    return render_template('order-ui.html', orders=orders)

@app.route('/add-order', methods=['POST'])
def add_order():
    order_data = request.json
    orders.append(order_data)  # Add the order to the in-memory list
    print(order_data)
    return jsonify({"message": "Order received!"}), 200

if __name__ == "__main__":
    app.run(port=3000)
