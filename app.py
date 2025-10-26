import os
import logging
from openai import OpenAI

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler, ContextTypes
)
from config import (
    TELEGRAM_TOKEN, OPENAI_API_KEY,
    LLM_MODEL, SYSTEM_PROMPTS, SUPPORTED_LANGUAGES
)
from database import db
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Track user sessions and language preferences
user_sessions = {}

def get_language_keyboard():
    """Create language selection keyboard"""
    keyboard = []
    row = []
    for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
        row.append(InlineKeyboardButton(lang_name, callback_data=f'lang_{lang_code}'))
        if len(row) == 2:  # 2 buttons per row
            keyboard.append(row)
            row = []
    if row:  # Add any remaining buttons
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    # Initialize user session
    user_id = update.effective_user.id
    user_sessions[user_id] = {'language': 'en'}  # Default to English
    
    welcome_messages = {
        'en': (
            "👋 *Welcome to Askia, your Kenyan knowledge assistant!*\n\n"
            "Please select your preferred language:"
        ),
        'sw': (
            "👋 *Karibu kwa Askia, msaidizi wako wa maarifa ya Kenya!*\n\n"
            "Tafadhali chagua lugha unayopendelea:"
        )
    }
    
    # Send language selection
    await update.message.reply_text(
        welcome_messages['en'],  # Default to English for language selection
        parse_mode='Markdown',
        reply_markup=get_language_keyboard()
    )
    
    # Log the new user
    logger.info(f"New user started the bot: {user_id}")

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang_code = query.data.replace('lang_', '')
    
    if lang_code not in SUPPORTED_LANGUAGES:
        lang_code = 'en'  # Default to English if invalid language code
    
    # Update user's language preference
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['language'] = lang_code
    
    # Confirmation messages in selected language
    confirm_messages = {
        'en': f"✅ Language set to English. How can I help you today?",
        'sw': f"✅ Lugha imewekwa kwa Kiswahili. Ninaweza kukusaidia nini leo?"
    }
    
    # Create main menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("🌾 Ask About Agriculture", callback_data='agriculture'),
            InlineKeyboardButton("🏥 Ask About Health", callback_data='health')
        ],
        [
            InlineKeyboardButton("🌍 Change Language", callback_data='change_language'),
            InlineKeyboardButton("❓ Help", callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        confirm_messages[lang_code],
        reply_markup=reply_markup
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language change request"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    current_lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    messages = {
        'en': "🌍 Please select your preferred language:",
        'sw': "🌍 Tafadhali chagua lugha unayopendelea:"
    }
    
    await query.edit_message_text(
        messages.get(current_lang, messages['en']),
        reply_markup=get_language_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and generate responses using RAG."""
    user_id = update.effective_user.id
    query = update.message.text
    
    # Get user's language preference (default to English)
    lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Show typing action
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action='typing'
    )
    
    # Get system prompt based on language
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS['en'])
    
    # Search for relevant documents
    results = db.search(query, k=3)
    
    # Format context from search results
    context = "\n\n".join([doc['text'] for doc in results])
    
    # Prepare messages for the chat completion
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]
    
    try:
        # Generate response using OpenAI
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Send the response
        response_text = response.choices[0].message.content.strip()
        await update.message.reply_text(response_text)
        
    except Exception as e:
        error_messages = {
            'en': "❌ Sorry, I encountered an error processing your request. Please try again.",
            'sw': "❌ Samahani, kumekuwa na tatizo katika kukamilisha ombi lako. Tafadhali jaribu tena."
        }
        await update.message.reply_text(error_messages.get(lang, error_messages['en']))
        logger.error(f"Error generating response: {str(e)}")

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle help button click"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Help messages in different languages
    help_messages = {
        'en': (
            "🤖 *Askia Help*\n\n"
            "I'm here to help you with information about Kenya. Here's what I can do:\n\n"
            "• Ask me anything about health, agriculture, or general knowledge\n"
            "• I'll provide answers based on my knowledge base\n"
            "• Use /language to change the language\n"
            "• Use /start to see the welcome message\n\n"
            "Try asking:\n"
            "• *Health:* What are the symptoms of malaria?\n"
            "• *Agriculture:* How do I grow maize in Kenya?\n"
            "• *General:* Tell me about community health workers"
        ),
        'sw': (
            "🤖 *Msaada wa Askia*\n\n"
            "Niko hapa kukusaidia kuhusu mambo mbalimbali nchini Kenya. Hivi ndivyo naweza kukusaidia:\n\n"
            "• Niulize kuhusu afya, kilimo, au maarifa ya jumla\n"
            "• Nitakujibu kulingana na kumbukumbu yangu\n"
            "• Tumia /language kubadilisha lugha\n"
            "• Tumia /start kuona ujumbe wa kukaribisha\n\n"
            "Jaribu kuniuliza:\n"
            "• *Afya:* Je, ni dalili gani za malaria?\n"
            "• *Kilimo:* Naweza kupanda mahindi vipi Kenya?\n"
            "• *Jumla:* Nipe maelezo kuhusu wafanyakazi wa afya ya jamii"
        )
    }
    
    # Create back button
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        help_messages.get(lang, help_messages['en']),
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back button click"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Main menu message
    messages = {
        'en': "How can I help you today?",
        'sw': "Ninaweza kukusaidia nini leo?"
    }
    
    # Create main menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("🌾 Ask About Agriculture", callback_data='agriculture'),
            InlineKeyboardButton("🏥 Ask About Health", callback_data='health')
        ],
        [
            InlineKeyboardButton("🌍 Change Language", callback_data='change_language'),
            InlineKeyboardButton("❓ Help", callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        messages.get(lang, messages['en']),
        reply_markup=reply_markup
    )

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str) -> None:
    """Handle topic selection (agriculture or health)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    # Topic messages in different languages
    topic_messages = {
        'agriculture': {
            'en': "🌾 *Agriculture*\n\nWhat would you like to know about agriculture in Kenya?\n\n"
                  "You can ask about:\n"
                  "• Crop cultivation\n"
                  "• Pest control\n"
                  "• Best farming practices\n"
                  "• And more...",
            'sw': "🌾 *Kilimo*\n\nUngependa kujua nini kuhusu kilimo nchini Kenya?\n\n"
                  "Unaweza kuuliza kuhusu:\n"
                  "• Ulimaji wa mazao\n"
                  "• Udhibiti wa wadudu\n"
                  "• Mbinu bora za kilimo\n"
                  "Na zaidi..."
        },
        'health': {
            'en': "🏥 *Health*\n\nWhat health-related information are you looking for?\n\n"
                  "You can ask about:\n"
                  "• Common illnesses\n"
                  "• Preventive measures\n"
                  "• First aid\n"
                  "And more...",
            'sw': "🏥 *Afya*\n\nUnatafuta taarifa gani kuhusu afya?\n\n"
                  "Unaweza kuuliza kuhusu:\n"
                  "• Magonjwa ya kawaida\n"
                  "• Hatua za kuzuia magonjwa\n"
                  "• Huduma ya kwanza\n"
                  "Na zaidi..."
        }
    }
    
    # Create back button
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the appropriate message based on the topic
    await query.edit_message_text(
        topic_messages[topic].get(lang, topic_messages[topic]['en']),
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user_id = update.effective_user.id
    lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    help_messages = {
        'en': (
            "🤖 *Askia Help*\n\n"
            "I'm here to help you with information about Kenya. Here's what I can do:\n\n"
            "• Ask me anything about health, agriculture, or general knowledge\n"
            "• I'll provide answers based on my knowledge base\n"
            "• Use /language to change the language\n"
            "• Use /start to see the welcome message\n\n"
            "Try asking:\n"
            "• *Health:* What are the symptoms of malaria?\n"
            "• *Agriculture:* How do I grow maize in Kenya?\n"
            "• *General:* Tell me about community health workers"
        ),
        'sw': (
            "🤖 *Msaada wa Askia*\n\n"
            "Niko hapa kukusaidia kuhusu mambo mbalimbali nchini Kenya. Hivi ndivyo naweza kukusaidia:\n\n"
            "• Niulize kuhusu afya, kilimo, au maarifa ya jumla\n"
            "• Nitakujibu kulingana na kumbukumbu yangu\n"
            "• Tumia /language kubadilisha lugha\n"
            "• Tumia /start kuona ujumbe wa kukaribisha\n\n"
            "Jaribu kuniuliza:\n"
            "• *Afya:* Je, ni dalili gani za malaria?\n"
            "• *Kilimo:* Naweza kupanda mahindi vipi Kenya?\n"
            "• *Jumla:* Nipe maelezo kuhusu wafanyakazi wa afya ya jamii"
        )
    }
    
    await update.message.reply_text(
        help_messages.get(lang, help_messages['en']),
        parse_mode='Markdown'
    )
    
    # Log the help command usage
    logger.info(f"User {user_id} requested help in {lang}")

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /language command to change the bot's language."""
    user_id = update.effective_user.id
    current_lang = user_sessions.get(user_id, {}).get('language', 'en')
    
    messages = {
        'en': "🌍 Please select your preferred language:",
        'sw': "🌍 Tafadhali chagua lugha unayopendelea:"
    }
    
    await update.message.reply_text(
        messages.get(current_lang, messages['en']),
        reply_markup=get_language_keyboard()
    )
    
    # Log the language change request
    logger.info(f"User {user_id} requested language change")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(change_language, pattern='^change_language$'))
    application.add_handler(CallbackQueryHandler(lambda u, c: handle_topic(u, c, 'agriculture'), pattern='^agriculture$'))
    application.add_handler(CallbackQueryHandler(lambda u, c: handle_topic(u, c, 'health'), pattern='^health$'))
    application.add_handler(CallbackQueryHandler(handle_help, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(handle_back, pattern='^back_to_main$'))
    
    # Add message handler (must be added last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Log errors
    application.add_error_handler(error_handler)
    
    # Start the Bot
    logger.info("Starting Askia bot...")
    print("Starting Askia bot...")
    application.run_polling()

# Add error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and send a message to the user."""
    # Log the full error
    logger.error(f"Error: {context.error}", exc_info=context.error)
    
    # Try to get the user's language preference
    lang = 'en'  # Default to English
    try:
        if update.effective_user:
            user_id = update.effective_user.id
            lang = user_sessions.get(user_id, {}).get('language', 'en')
    except Exception as e:
        logger.error(f"Error getting user language in error handler: {e}")
    
    # Error messages in different languages
    error_messages = {
        'en': (
            "❌ *Oops! Something went wrong.*\n\n"
            "I encountered an error while processing your request. "
            "Please try again in a few moments. If the problem persists, "
            "you can use /help for assistance."
        ),
        'sw': (
            "❌ *Lo santa! Kuna kosa limetokea.*\n\n"
            "Nimekutana na kosa wakati wa kukamilisha ombi lako. "
            "Tafadhali jaribu tena baada ya muda mfupi. Ikiwa tatizo linaendelea, "
            "unaweza kutumia /msaada kwa usaidizi."
        )
    }
    
    # Send the error message to the user
    try:
        if update.effective_message:
            await update.effective_message.reply_text(
                error_messages.get(lang, error_messages['en']),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")

# Main entry point
if __name__ == "__main__":
    main()
