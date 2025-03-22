import logging
import re
from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_USER_IDS
from bot.utils import extract_aliexpress_links, is_valid_aliexpress_link
from bot.aliexpress import get_product_details, convert_to_affiliate_link
from bot.analytics import log_user_action, get_statistics

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = Router()

# Command handlers
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Send welcome message when the command /start is issued."""
    log_user_action(message.from_user.id, "start_command")
    
    await message.answer(
        f"👋 Welcome to Ali Best Price Bot!\n\n"
        f"I can help you find the best prices on AliExpress and generate affiliate links.\n\n"
        f"Just send me an AliExpress product link, and I'll do the rest! 🛍️"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Send help message when the command /help is issued."""
    log_user_action(message.from_user.id, "help_command")
    
    await message.answer(
        "🔍 <b>How to use Ali Best Price Bot:</b>\n\n"
        "1. Send me any AliExpress product link\n"
        "2. I'll check the price and generate an affiliate link\n"
        "3. Use the affiliate link to support us!\n\n"
        "<b>Commands:</b>\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "If you have any issues, please try again later.",
        parse_mode="HTML"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Send statistics when the command /stats is issued (admin only)."""
    if message.from_user.id not in ADMIN_USER_IDS and ADMIN_USER_IDS:
        await message.answer("⛔ This command is for administrators only.")
        return
    
    log_user_action(message.from_user.id, "stats_command")
    
    stats = get_statistics()
    
    stats_message = (
        "📊 <b>Bot Statistics:</b>\n\n"
        f"Total Users: {stats['total_users']}\n"
        f"Total Requests: {stats['total_requests']}\n"
        f"Successful Conversions: {stats['successful_conversions']}\n"
        f"Failed Conversions: {stats['failed_conversions']}\n"
        f"Active Today: {stats['active_today']}\n"
        f"Active This Week: {stats['active_this_week']}"
    )
    
    await message.answer(stats_message, parse_mode="HTML")

# Message handlers
@router.message(F.text)
async def process_message(message: Message):
    """Process messages with AliExpress links."""
    log_user_action(message.from_user.id, "message_received")
    
    # Extract AliExpress links from the message
    links = extract_aliexpress_links(message.text)
    
    if not links:
        await message.answer(
            "🔍 I couldn't find any valid AliExpress links in your message.\n\n"
            "Please send me a valid AliExpress product link like:\n"
            "https://aliexpress.com/item/1234567890.html"
        )
        return
    
    # Process the first valid link
    for link in links:
        if is_valid_aliexpress_link(link):
            await process_aliexpress_link(message, link)
            break
    else:
        await message.answer(
            "⚠️ The link you sent doesn't appear to be a valid AliExpress product link.\n\n"
            "Please check the link and try again."
        )

async def process_aliexpress_link(message: Message, link: str):
    """Process a valid AliExpress link."""
    # Send a processing message
    processing_msg = await message.answer("🔍 Processing your AliExpress link...")
    
    try:
        # Get product details
        product = await get_product_details(link)
        
        if not product:
            await processing_msg.edit_text(
                "❌ Sorry, I couldn't retrieve information for this product.\n\n"
                "This might be due to:\n"
                "- The product is no longer available\n"
                "- The link is incorrect\n"
                "- AliExpress API limitations\n\n"
                "Please try another product link."
            )
            log_user_action(message.from_user.id, "product_not_found")
            return
        
        # Generate affiliate link
        affiliate_link = await convert_to_affiliate_link(link)
        
        # Build the response
        response = (
            f"🛍️ <b>{product['title']}</b>\n\n"
            f"💰 <b>Current Price:</b> ${product['price']}\n"
        )
        
        if product.get('original_price') and product['original_price'] > product['price']:
            discount = round(((product['original_price'] - product['price']) / product['original_price']) * 100)
            response += f"🏷️ <b>Original Price:</b> ${product['original_price']} (Save {discount}%)\n"
        
        if product.get('shipping_cost') is not None:
            if product['shipping_cost'] > 0:
                response += f"🚚 <b>Shipping:</b> ${product['shipping_cost']}\n"
            else:
                response += f"🚚 <b>Shipping:</b> Free\n"
        
        if product.get('rating'):
            response += f"⭐ <b>Rating:</b> {product['rating']}/5\n"
        
        response += f"\n🔗 <b>Affiliate Link:</b>\n{affiliate_link}"
        
        # Create inline keyboard
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🛒 Open in AliExpress", url=affiliate_link)
        
        # Send the response
        await processing_msg.edit_text(
            response,
            parse_mode="HTML",
            disable_web_page_preview=False,
            reply_markup=keyboard.as_markup()
        )
        
        log_user_action(message.from_user.id, "link_processed_successfully")
        
    except Exception as e:
        logger.error(f"Error processing link {link}: {e}")
        await processing_msg.edit_text(
            "❌ Sorry, something went wrong while processing your link.\n\n"
            "Please try again later or try a different product link."
        )
        log_user_action(message.from_user.id, "error_processing_link")

# Error handlers
@router.error(ExceptionTypeFilter(TelegramAPIError))
async def handle_telegram_api_error(event, error):
    """Handle Telegram API errors."""
    logger.error(f"Telegram API error: {error}")
    message = getattr(event, "message", None)
    if message:
        await message.answer(
            "❌ An error occurred while communicating with Telegram.\n"
            "Please try again later."
        )

@router.error()
async def handle_unknown_error(event, error):
    """Handle unknown errors."""
    logger.error(f"Unknown error: {error}")
    message = getattr(event, "message", None)
    if message:
        await message.answer(
            "❌ An unexpected error occurred.\n"
            "Please try again later."
        )

def register_handlers(dp: Dispatcher):
    """Register all handlers with the dispatcher."""
    # Check if the router is already attached to avoid errors
    if not hasattr(router, "_parent_router"):
        dp.include_router(router)
