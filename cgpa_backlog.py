import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    ConversationHandler, 
    MessageHandler, 
    filters,
    CallbackQueryHandler
)
from telegram.constants import ChatMemberStatus
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# 1. Load credentials
load_dotenv()
TOKEN = os.getenv("Token")
raw_id = os.getenv("GROUP_ID")
GROUP_ID = int(raw_id) if raw_id else -100123456789 # Fallback ID

# 2. Define Conversation States
NAME, USN, DEPT, CGPA,BACKLOGS = range(5)

# --- HANDLER FUNCTIONS ---

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        allowed_statuses = [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        
        if member.status in allowed_statuses:
            await update.message.reply_text("✅ Access Granted! Please enter your name:")
            return NAME 
        else:
            await update.message.reply_text("❌ Access Denied. You are not in the group.")
            return ConversationHandler.END
            
    except Exception as e:
        await update.message.reply_text("⚠️ Error: I can't check membership. Am I an admin?")
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data['name'] = user_name  # Save the name for later
    await update.message.reply_text(f"Nice to meet you, {user_name}! Now, please enter your USN:")
    return USN

async def get_usn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_usn = update.message.text
    context.user_data['usn'] = user_usn
    
    # Define the buttons
    keyboard = [
        [
            InlineKeyboardButton("CSE Core", callback_data='CSE Core'),
            InlineKeyboardButton("CSE:AI ML", callback_data='CSE:AI ML'),
        ],
        [
            InlineKeyboardButton("Cyber Security", callback_data='Cyber Security'),
            InlineKeyboardButton("Physiotherapy", callback_data='Physiotherapy'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Your USN has been successfully saved! Now, please select your Department:",
        reply_markup=reply_markup
    )
    return DEPT

async def handle_dept_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['dept'] = query.data
    await query.edit_message_text(text=f"Registration complete! Name: {context.user_data['name']}, USN: {context.user_data['usn']}, Dept: {query.data}")
    await query.message.reply_text("Department saved! Now, please enter your current CGPA:")
    return CGPA

async def cancel_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration cancelled.")
    return ConversationHandler.END

async def get_cgpa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cgpa = update.message.text
    # Simple validation check
    try:
        float_cgpa = float(cgpa)
        context.user_data['cgpa'] = float_cgpa
        await update.message.reply_text("Got it. Finally, how many active backlogs do you have? (Enter 0 if none):")
        return BACKLOGS
    except ValueError:
        await update.message.reply_text("Please enter a valid number for CGPA (e.g., 7.8).")
        return CGPA

async def get_backlogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    backlogs = update.message.text
    context.user_data['backlogs'] = backlogs
    
    summary = (
        "✅ **Registration Complete!**\n\n"
        f"👤 Name: {context.user_data.get('name')}\n"
        f"🆔 USN: {context.user_data.get('usn')}\n"
        f"🏢 Dept: {context.user_data.get('dept')}\n"
        f"📈 CGPA: {context.user_data.get('cgpa')}\n"
        f"🚫 Backlogs: {backlogs}"
    )
    
    await update.message.reply_text(summary, parse_mode='Markdown')
    return ConversationHandler.END

def main():

    application = ApplicationBuilder().token(TOKEN).build()

    registration_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_registration)],
        states={
            
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            USN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_usn)],
            DEPT: [CallbackQueryHandler(handle_dept_selection)],
            CGPA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cgpa)],      
            BACKLOGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_backlogs)], 
        },
        
        fallbacks=[CommandHandler('cancel', cancel_op)],
    )

    application.add_handler(registration_conv)
    
    print("The bot is successfully running...")
    application.run_polling()

if __name__ == '__main__':
    main()
