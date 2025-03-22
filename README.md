# Ali Best Price Telegram Bot

This is a Telegram bot that allows users to find the best prices on AliExpress and generate affiliate links. The bot is built using Python and the aiogram library, and it's designed to be deployed on Vercel.

## Features

- **Start Command** (`/start`): Sends a welcome message with instructions.
- **Help Command** (`/help`): Provides help and usage instructions.
- **Link Processing**: Detects and extracts valid AliExpress product links from user messages.
- **API Integration**: Uses the AliExpress API to fetch product details, including the best price, shipping details, and available discounts.
- **Affiliate Conversion**: Converts regular product links into affiliate links using your AliExpress AppKey and App Secret.
- **Price Comparison**: Shows original price vs. current price when a discount is available.
- **Admin Commands** (`/stats`): Provides basic usage statistics for administrators.
- **Error Handling**: Returns friendly messages if product links are invalid or API requests fail.

## How It Works

1. The user sends a message containing an AliExpress product link to the bot.
2. The bot extracts the product ID from the link and fetches product details from the AliExpress API.
3. The bot converts the original link to an affiliate link using the AliExpress Affiliate API.
4. The bot returns the product information and affiliate link to the user.

## Project Structure

```
├── bot
│   ├── __init__.py
│   ├── aliexpress.py     # AliExpress API integration
│   ├── analytics.py      # User activity tracking and statistics
│   ├── handlers.py       # Telegram message handlers
│   └── utils.py          # Utility functions
├── .env.example          # Example environment variables
├── config.py             # Configuration settings
├── main.py               # Main application entry point
└── vercel.json           # Vercel deployment configuration
```

## Setup and Deployment

### Prerequisites

- Python 3.11 or higher
- A Telegram bot token (obtain from @BotFather)
- AliExpress API credentials (AppKey and App Secret)

### Local Development

1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` and fill in your credentials
4. Run the bot:
   ```
   python main.py
   ```

### Downloading and Hosting on GitHub

1. Download this project from Replit:
   - From the Replit project page, click on the three dots in the upper right corner
   - Select "Download as zip"
   - Extract the zip file to your local machine

2. Create a new GitHub repository:
   - Go to GitHub and log in to your account
   - Click on the "+" icon in the upper right corner and select "New repository"
   - Name your repository (e.g., "ali-best-price-bot")
   - Make it public or private based on your preference
   - Click "Create repository"

3. Push the code to your GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ali-best-price-bot.git
   git push -u origin main
   ```

### Deployment on Vercel

1. Connect your GitHub repository to Vercel:
   - Go to [Vercel](https://vercel.com/) and log in or create an account
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Select the repository containing your bot code

2. Configure the Vercel deployment:
   - Framework Preset: Select "Other"
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r vercel-requirements.txt`

3. Add the following environment variables in Vercel project settings:
   - `BOT_TOKEN`: Your Telegram bot token
   - `ALIEXPRESS_APP_KEY`: Your AliExpress App Key
   - `ALIEXPRESS_APP_SECRET`: Your AliExpress App Secret
   - `BASE_WEBHOOK_URL`: Your Vercel app URL (e.g., https://ali-best-price-bot.vercel.app)
   - `ADMIN_USER_IDS`: Comma-separated list of admin Telegram user IDs

4. Deploy the project by clicking "Deploy"

5. Set up the Telegram bot webhook:
   - After deployment, visit your Vercel app URL + "/webhook" to verify that it works
   - Use the Telegram Bot API to set the webhook:
     ```
     https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={VERCEL_APP_URL}/webhook
     ```
     (Replace `{BOT_TOKEN}` with your actual bot token and `{VERCEL_APP_URL}` with your Vercel app URL)

## Usage

1. Start a chat with the bot on Telegram
2. Send the command `/start` to get started
3. Send any AliExpress product link to the bot
4. The bot will respond with product details and an affiliate link

## Technical Details

- **Webhook Mode**: The bot uses webhook mode for production deployment, which is more suitable for serverless environments like Vercel.
- **Rate Limiting**: Includes built-in rate limiting to avoid exceeding AliExpress API limits.
- **Error Handling**: Comprehensive error handling for API failures and invalid links.
- **Analytics**: Basic analytics tracking for monitoring bot usage and performance.

## License

MIT