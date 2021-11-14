from typing import BinaryIO
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "secret"

DB_HOST = "localhost"
DB_NAME = "test"
DB_USER = "postgres"
DB_PASS = "x"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

## /customer end point is used to view customers as json 
## and also used to query for youngest customers

@app.route('/customer', methods = ['POST','GET'])
def view_customer():
    if request.method == 'GET':
        user = request.args.get('number')
        if user==None:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                s = "SELECT * FROM customer ORDER BY id"
                cur.execute(s)
                list_cust = cur.fetchall()
                content = {}
                customer = []
                for result in list_cust:
                    content = {'id' : result['id'], 'name' : result['name'], 'dob' : result['dob']}
                    customer.append(content)
                    content = {}

                return jsonify(customer)
            except:
                conn.rollback()
                return render_template('index.html')
        else:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""SELECT * FROM customer ORDER BY dob DESC LIMIT %s""", user)
                list_cust = cur.fetchall()
                return render_template('customer.html', list_cust = list_cust)
            except:
                conn.rollback()
                return "Invalid input"
    else:
        return render_template('customer.html')


## /order end point is used to view orders as json and
## also used to view orders by specific customers

@app.route('/order', methods = ['POST','GET'])
def view_order():
    if request.method == 'GET':
        user = request.args.get('customer_id')
        if user == None:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                s = "SELECT * FROM orders ORDER BY datetime ASC"
                cur.execute(s)
                list_orders = cur.fetchall()
                content = {}
                orders = []
                for result in list_orders:
                    content = {'order_id' : result['order_id'], 'item_id' : result['item_id'], 'item_name' : result['item_name'], 'item_price' : result['item_price'], 'datetime' : result['datetime'], 'customer_id' : result['customer_id']}
                    orders.append(content)
                    content = {}
                return jsonify(orders)
            except:
                conn.rollback()
                return render_template('index.html')
        else:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""SELECT * FROM orders WHERE customer_id = %s""", user)
                list_orders = cur.fetchall()
                return render_template('orders.html', list_orders = list_orders)
            except:
                conn.rollback()
                return "Invalid input"
    else:
        return render_template('orders.html')


## /items end point is used to view items available for purchase
## as json

@app.route('/items')
def view_items():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM items ORDER BY item_id"
    cur.execute(s)
    list_orders = cur.fetchall()
    content = {}
    orders = []
    for result in list_orders:
        content = {'item_id' : result['item_id'], 'item_name' : result['item_name'], 'item_price' : result['item_price']}
        orders.append(content)
        content = {}
    return jsonify(orders)


## /customer/create end point is used to create a new customer

@app.route('/customer/create', methods=['POST','GET'])
def create_customer():
    if request.method == 'POST':
        cid = request.form['cid']
        cname = request.form['cname']
        dob = request.form['dob']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute("""INSERT INTO customer VALUES (%s, %s, %s)""", (cid,cname,dob))
            flash('Customer created successfully')
            conn.commit()
            return redirect(url_for('index'))
        except:
            conn.rollback()
            return "Invalid input"
    else:
        return render_template('createCus.html')


## /order/create end point is use to create a new order

@app.route('/order/create', methods=['POST','GET'])
def create_order():
    if request.method == 'POST':
        Oid = request.form['Oid']
        Iid = request.form['Iid']
        cid = request.form['cID2']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute("""INSERT INTO orders(order_id, item_id, item_name, item_price, customer_id)
                            VALUES (%s,%s,(SELECT item_name
				                            FROM items
				                            WHERE item_id = %s),
                                            (SELECT item_price
									        FROM items
									        WHERE item_id = %s),
                                            (SELECT id
		                                    FROM customer
		                                    WHERE id = %s))""", (Oid, Iid, Iid, Iid, cid))
            flash('Order created successfully')
            conn.commit()
            return redirect(url_for('index'))
        except:
            conn.rollback()
            return "Invalid input"
    else:
        return render_template('createOrd.html')
        
if __name__ == "__main__":
    app.run(debug=True)
