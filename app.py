import logging
import os
from flask import Flask, render_template_string, jsonify
from config import BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Default route
@app.route('/')
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ali Best Price Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background-color: var(--bs-body-bg);
                color: var(--bs-body-color);
            }
            .container {
                max-width: 600px;
                padding: 2rem;
            }
        </style>
    </head>
    <body data-bs-theme="dark">
        <div class="container">
            <div class="card">
                <div class="card-body">
                    <h1 class="card-title">Ali Best Price Bot</h1>
                    <p class="card-text">This is a Telegram bot that helps you find the best prices on AliExpress and generate affiliate links.</p>
                    <div class="alert alert-success">Server is running!</div>
                    <a href="https://t.me/Ali_Best_Price_bot" class="btn btn-primary">Open Bot in Telegram</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/api/status')
def status():
    return jsonify({
        "status": "Running", 
        "bot_name": "Ali Best Price Bot"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)