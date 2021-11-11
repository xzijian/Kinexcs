from typing import BinaryIO
from flask import Flask, render_template, url_for, request, redirect, jsonify
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

@app.route('/customer', methods = ['POST','GET'])
def view_customer():
    if request.method == 'GET':
        user = request.args.get('number')
        if user==None:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            s = "SELECT * FROM customer ORDER BY id"
            cur.execute(s)
            list_cust = cur.fetchall()
            #return render_template('customer.html', list_cust = list_cust)
            #return jsonify(json_list = list_cust)
            content = {}
            customer = []
            for result in list_cust:
                content = {'id' : result['id'], 'name' : result['name'], 'dob' : result['dob']}
                customer.append(content)
                content = {}

            return jsonify(customer)
        else:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""SELECT * FROM customer ORDER BY dob DESC LIMIT %s""", user)
                list_cust = cur.fetchall()
                return render_template('customer.html', list_cust = list_cust)
            except:
                conn.rollback()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                s = "SELECT * FROM customer ORDER BY id"
                cur.execute(s)
                list_cust = cur.fetchall()
                return render_template('customer.html', list_cust = list_cust)
    elif request.headers['Content-Type'] == 'application/json':
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM customer ORDER BY id"
        cur.execute(s)
        list_cust = cur.fetchall()
        #return render_template('customer.html', list_cust = list_cust)
        #return jsonify(json_list = list_cust)
        content = {}
        customer = []
        for result in list_cust:
            content = {'id' : result['id'], 'name' : result['name'], 'dob' : result['dob']}
            customer.append(content)
            content = {}

        return jsonify(customer)

@app.route('/order')
def view_order():
    if request.method == 'GET':
        user = request.args.get('customer_id')
        if user == None:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            s = "SELECT * FROM orders ORDER BY datetime ASC"
            cur.execute(s)
            list_orders = cur.fetchall()
            #return render_template('orders.html', list_orders = list_orders)
            content = {}
            orders = []
            for result in list_orders:
                content = {'item_name' : result['item_name'], 'item_price' : result['item_price'], 'datetime' : result['datetime'], 'customer_id' : result['customer_id']}
                orders.append(content)
                content = {}

            return jsonify(orders)
        else:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""SELECT * FROM orders WHERE customer_id = %s""", user)
                list_orders = cur.fetchall()
                return render_template('orders.html', list_orders = list_orders)
            except:
                conn.rollback()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                s = "SELECT * FROM orders ORDER BY datetime DESC"
                cur.execute(s)
                list_orders = cur.fetchall()
                return render_template('orders.html', list_orders = list_orders)
    else:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM orders ORDER BY datetime ASC"
        cur.execute(s)
        list_orders = cur.fetchall()
        #return render_template('orders.html', list_orders = list_orders)
        content = {}
        orders = []
        for result in list_orders:
            content = {'item_name' : result['item_name'], 'item_price' : result['item_price'], 'datetime' : result['datetime'], 'customer_id' : result['customer_id']}
            orders.append(content)
            content = {}

        return jsonify(orders)

@app.route('/customer/create', methods=['POST','GET'])
def create_customer():
    if request.method == 'POST':
        cid = request.form['cid']
        cname = request.form['cname']
        dob = request.form['dob']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute("""INSERT INTO customer VALUES (%s, %s, %s)""", (cid,cname,dob))
            return render_template('index.html')
        except:
            conn.rollback()
            return "Invalid input"
    else:
        return render_template('createCus.html')


if __name__ == "__main__":
    app.run(debug=True)
