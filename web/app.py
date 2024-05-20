# app.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

#@app.route('/create_account', methods=['POST'])
#def create_account():
    # Handle the account creation logic here
    private_key = request.form.get('private_key')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Example: Check if passwords match (Replace with your actual validation logic)
    if password == confirm_password:
        # Redirect to the account created page if successful
        return redirect(url_for('account_created'))
    else:
        # Handle the case where passwords don't match (e.g., show an error message)
        return render_template('error.html', message='Passwords do not match')

@app.route('/login', methods=['POST'])
def welcome():
    return render_template('login.html')

#@app.route('/login', methods=['POST'])
#def welcome():
    render_template('login.html')
    private_key = request.form.get('Private Key')
    password = request.form.get('password')

    # Replace this with your actual authentication logic.
    # Check if private_key and password match a user in your database.
    if private_key == 'asd' and password == 'asd':
        user_id = 'admin'  # Replace with the actual user ID or username
        return redirect(url_for('admindashboard'))
    else:
        return render_template('login.html', error='Invalid credentials')


@app.route('/create_account')
def page2():
    return render_template('create.html')






if __name__ == '__main__':
    app.run(debug=True)
