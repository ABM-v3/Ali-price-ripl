import logging
import os
from flask import Flask, request, render_template_string, jsonify
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from bot.handlers import register_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Register all handlers
register_handlers(dp)

# Initialize Flask application
app = Flask(__name__)

# Webhook route for Telegram bot
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    """Process webhook updates from Telegram"""
    if request.headers.get('content-type') == 'application/json':
        update = request.get_json()
        
        try:
            # Process the update
            # Note: Properly we'd use a task queue or async framework
            # But for demo purposes, we'll just log it
            logger.info(f"Received update: {update}")
            return jsonify({"status": "ok"})
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return jsonify({"status": "error", "message": str(e)})
    
    return jsonify({"status": "error", "message": "Invalid content type"})

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

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response status: {response.status_code}")
    return response

@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# For local development
if __name__ == "__main__":
    # For local development, we'll use polling mode instead of webhook
    async def main():
        logger.info("Starting bot in polling mode...")
        await dp.start_polling(bot, skip_updates=True)
    
    import asyncio
    asyncio.run(main())
