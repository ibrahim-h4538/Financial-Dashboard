from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import csv
from datetime import datetime

app = Flask(__name__)

# Define data as a global variable
data = None

# Function to load financial data from the CSV file
def load_data():
    global data  # Access the global variable
    data = pd.read_csv('financial_data.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    return data

# Function to generate and return the chart as a base64-encoded image
def generate_plot(data):
    plt.figure(figsize=(12, 6))
    plt.plot(data['Date'], data['Revenue'], marker='o', color='blue')
    plt.title('Revenue Over Time')
    plt.xlabel('Date')
    plt.ylabel('Revenue')
    plt.tight_layout()
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    return chart_url

# Initial load of financial data
load_data()

@app.route('/')
def dashboard():
    chart_url = generate_plot(data)
    error_message = None  # Initialize error_message
    
    if request.args.get('error'):
        error_message = "Date must be after the previous data."
        last_added_date = data['Date'].max().strftime('%d %B %Y')  # Format the date as day month year
        return render_template('dashboard.html', chart_url=chart_url, error_message=error_message, last_added_date=last_added_date)
    
    return render_template('dashboard.html', chart_url=chart_url, error_message=error_message)

@app.route('/input', methods=['GET', 'POST'])
def input_form():
    if request.method == 'POST':
        # Get form data
        date_str = request.form['date']
        revenue = float(request.form['revenue'])
        expenses = float(request.form['expenses'])
        
        # Converts the entered date to a datetime object
        entered_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Checks if the entered date is earlier than the latest date in the existing data
        latest_date = data['Date'].max()
        if entered_date < latest_date:
            return redirect(url_for('dashboard', error=True))
        
        # Appends the data to the CSV file
        with open('financial_data.csv', mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            # Write the data as a new row in the CSV file
            writer.writerow([date_str, revenue, expenses, revenue - expenses])
        
        # Reloads the financial data
        load_data()
        
        # Redirect to the dashboard
        return redirect(url_for('dashboard'))
    
    return render_template('input_form.html')

if __name__ == '__main__':
    app.run(debug=True)