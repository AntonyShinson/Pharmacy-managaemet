import streamlit as st
import pandas as pd
import sqlite3

# Database connection code
conn = sqlite3.connect("drug_data.db", check_same_thread=False)
c = conn.cursor()

# Create
c.execute('''CREATE TABLE IF NOT EXISTS Customers (
                C_Name TEXT NOT NULL,
                C_Password TEXT NOT NULL,
                C_Email TEXT PRIMARY KEY NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS Drugs (
                D_id INTEGER PRIMARY KEY AUTOINCREMENT,
                D_Name TEXT UNIQUE NOT NULL,
                D_ExpDate TEXT NOT NULL,
                D_Qty INTEGER NOT NULL,
                D_Price REAL NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS Orders (
                O_id INTEGER PRIMARY KEY AUTOINCREMENT,
                O_Name TEXT NOT NULL,
                O_Items TEXT NOT NULL,
                O_Qty INTEGER NOT NULL,
                O_TotalPrice REAL NOT NULL)''')

conn.commit()

# Initialize
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "cart" not in st.session_state:
    st.session_state.cart = {}

# ADMIN PAGE
def admin_page():
    st.title("Admin Dashboard")
    
    name = st.text_input("Medicine Name")
    qty = st.number_input("Quantity", min_value=1, step=1)
    price = st.number_input("Price per unit", min_value=0.01, step=0.01)
    expiry_date = st.date_input("Expiry Date")
    
    if st.button("Add Medicine"):
        try:
            c.execute('INSERT INTO Drugs (D_Name, D_Qty, D_Price, D_ExpDate) VALUES (?, ?, ?, ?)', 
                      (name, qty, price, expiry_date))
            conn.commit()
            st.success("Medicine added successfully!")
        except sqlite3.IntegrityError:
            st.error("Medicine already exists!")
    
    st.subheader("Available Medicines")
    meds = pd.read_sql_query("SELECT * FROM Drugs", conn)
    st.dataframe(meds)

#AUTHENTICATION-USER
def authenticate(username, password):
    c.execute('SELECT C_Password FROM Customers WHERE LOWER(C_Name) = LOWER(?)', (username,))
    result = c.fetchone()
    return result is not None and result[0] == password

def sign_up(username, password, email):
    try:
        c.execute('INSERT INTO Customers (C_Name, C_Password, C_Email) VALUES (?, ?, ?)',
                  (username, password, email))
        conn.commit()
        st.success("Sign-up successful! You can now log in.")
    except sqlite3.IntegrityError:
        st.error("Username or Email already exists. Please try another.")

# Customer dashboard
def customer_dashboard(username):
    st.title("Welcome to Your Dashboard")
    
    c.execute("SELECT D_Name, D_Qty, D_Price FROM Drugs WHERE D_Qty > 0")
    medicines = {row[0]: {'qty': row[1], 'price': row[2]} for row in c.fetchall()}
    
    if medicines:
        selected_product = st.selectbox("Select a medicine", ["Select"] + list(medicines.keys()))
        
        if selected_product != "Select":
            max_qty = medicines[selected_product]['qty']
            price = medicines[selected_product]['price']
            quantity = st.number_input(f"Enter quantity (Max {max_qty})", min_value=1, max_value=max_qty, step=1)
            
            if st.button("Add to Cart"):
                st.session_state.cart[selected_product] = {'qty': quantity, 'price': price * quantity}
                st.rerun()
        
        if st.session_state.cart:
            st.subheader("Shopping Cart")
            cart_df = pd.DataFrame.from_dict(st.session_state.cart, orient='index')
            st.dataframe(cart_df)
            
            total_price = sum(item['price'] for item in st.session_state.cart.values())
            st.write(f"**Total Price: ₹{total_price:.2f}**")
            
            if st.button("Place Order"):
                for med, details in st.session_state.cart.items():
                    c.execute('INSERT INTO Orders (O_Name, O_Items, O_Qty, O_TotalPrice) VALUES (?, ?, ?, ?)', 
                            (username, med, details['qty'], details['price']))
                    c.execute('UPDATE Drugs SET D_Qty = D_Qty - ? WHERE D_Name = ?', (details['qty'], med))
                
                conn.commit()
                
                st.success("Your order has been placed successfully!")
                st.subheader("Order Summary")
                st.dataframe(cart_df)
                st.write(f"**Total Price: ₹{total_price:.2f}**")
    else:
        st.warning("No medicines available.")

# SIDEBAR
menu = ["Login", "SignUp", "Admin"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Login":
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password", type='password')
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")
elif choice == "SignUp":
    sign_up(st.text_input("User Name"), st.text_input("Password", type='password'), st.text_input("Email"))
elif choice == "Admin":
    admin_page()

if "logged_in" in st.session_state and st.session_state.logged_in:
    customer_dashboard(st.session_state.username)
