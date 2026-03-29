import mysql.connector
from telegram.ext import ConversationHandler

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      
        user="root",  
        password="Root@12345",
        database="telegrambotdb"
    )

def finalize_registration(update, context):
    user_data = context.user_data
    # Capture the last piece of info (Active Backlogs) from the user input
    user_data['active_backlogs'] = update.message.text
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL Query updated to match your new table schema
        sql = """
            INSERT INTO Students (
                telegram_id, full_name, phone_number, usn, 
                department, cgpa, grad_year, active_backlogs
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                full_name=%s, phone_number=%s, usn=%s, 
                department=%s, cgpa=%s, grad_year=%s, active_backlogs=%s
        """
        
        # Mapping the data from user_data to the query
        # We pass the same values twice: once for INSERT, once for UPDATE
        registration_values = (
            update.message.from_user.id,
            user_data.get('full_name'),
            user_data.get('phone_number'),
            user_data.get('usn'),
            user_data.get('department'),
            user_data.get('cgpa'),
            user_data.get('grad_year'),
            user_data.get('active_backlogs')
        )
        
        # Combine the tuple for the UPDATE part of the query
        # (This avoids re-writing the same 7 variables manually)
        full_values = registration_values + registration_values[1:] 

        cursor.execute(sql, full_values)
        conn.commit()
        
        # Success Message
        update.message.reply_text(
            "✅ *REGISTRATION SUCCESSFUL!*\n\n"
            "Your profile has been saved to the placement database. "
            "You can use /register again at any time to update your CGPA or backlogs.",
            parse_mode='Markdown'
        )
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        update.message.reply_text("⚠️ There was a database error. Please contact an admin.")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return ConversationHandler.END
