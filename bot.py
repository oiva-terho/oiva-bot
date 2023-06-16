import os
from dotenv import dotenv_values
from datetime import datetime
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

env = dotenv_values(".env")
TOKEN = env["TOKEN"]
BOT_USERNAME = env["BOT_USERNAME"]

# List of authorized user IDs
authorized_users = [814447300]

# Directory to save received pictures and messages
save_directory = 'received-docs'
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Commands

async def start_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
  message = """Welcome, adventurer! Fame and fortune avait! \n\n
    To save document add it without compression and write it's name in format: \n
    Name_of_owner - Name_of_document \n\n
    To get it back write: \n
    Give (or Дай) Name_of_owner Name_of_document"""

  await update.message.reply_text(message)

async def help_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
  message = "Now we can:\n\n"
  possibilities = [
      "📸 Save your dos and photos",
      "📋 Organize your docs by names",
      "✉️ Keep a record of your thoughts",
  ]

  message += "\n".join(possibilities[:3])
  await update.message.reply_text(message)

# Saves document to this computer

async def save_doc(file_name, update: Update, context:ContextTypes.DEFAULT_TYPE):
  folder_name = file_name.split('-')[0].strip()

  subfolder_path = os.path.join(save_directory, folder_name)
  if not os.path.exists(subfolder_path):
    os.makedirs(subfolder_path)
  
  file = await context.bot.get_file(context.user_data['doc_id'])
  file_path = os.path.join(subfolder_path, f'{file_name}.jpg')

  if os.path.exists(file_path):
    await update.message.reply_text('File already exists. Should it be replaced?')
    await context.bot.send_document(chat_id=update.message.chat_id, document=file_path)
    context.user_data['conflict'] = file_path
    return
  
  await file.download_to_drive(file_path)
  del context.user_data['doc_id']
  await update.message.reply_text('Picture saved successfully.')
  return  

async def handle_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id in authorized_users:

      if update.message.photo:
        context.user_data['doc_id'] = update.message.photo[-1].file_id
      if update.message.document:
        context.user_data['doc_id'] = update.message.document.file_id
      if update.message.caption:
        doc_name = update.message.caption.strip()
        await save_doc(doc_name, update, context)
      else:
        await update.message.reply_text('Please enter name of the document')
        return 

# Responses

def handle_response(text: str) -> str:
  print(f'handle_response')
  proccesed: str = text.lower()
  if "save photo" or "save picture" in proccesed: 
    return "Upload it here and write the name under photo"
  return "Wait for a while, I don't have AI yet..."

async def handle_message (update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_type: str = update.message.chat.type
  user_id: str = update.message.from_user.id
  text: str = update.message.text

  if 'doc_id' in context.user_data:
    if 'conflict' in context.user_data:
      if text.lower() == "yes" or text.lower() == "да":
        file = await context.bot.get_file(context.user_data['doc_id'])
        await file.download_to_drive(context.user_data['conflict'])
        del context.user_data['doc_id']
        del context.user_data['conflict']
        return
      else: 
        del context.user_data['conflict']
        await update.message.reply_text('Enter another name')
    await save_doc(text, update, context)
    
    return
     
  save_message(text, user_id)

  if chat_type == 'group':
    if BOT_USERNAME in text:
      new_text: str = text.replace(BOT_USERNAME, '').strip()
      response: str = handle_response(new_text)
    else: return
  else: response: str = handle_response(text)
  save_message(response, user_id, True)

  await update.message.reply_text(response)

def save_message(text: str, user_id: str, bot=False):
   if user_id in authorized_users:
      now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

      save_path = os.path.join(save_directory, f'{user_id}.txt')
      if bot == False:
        with open(save_path, 'a') as file:
          file.write(f"{now} : {text}" + '\n')
      else:
        with open(save_path, 'a') as file:
          file.write(f"{now} : Bot: {text}" + '\n')

async def error (update: Update, context: ContextTypes.DEFAULT_TYPE):
  print(f'Update {update} \n err: {context.error}')

def main():
  print(f'bot started')

  app = Application.builder().token(TOKEN).build()

# Commands
  app.add_handler(CommandHandler('start', start_command)) 
  app.add_handler(CommandHandler('help', help_command)) 

# Messages
  app.add_handler(MessageHandler(filters.ATTACHMENT, handle_doc))
  app.add_handler(MessageHandler(filters.TEXT, handle_message))

# Error 
  app.add_error_handler(error)

# Polls the bot
  app.run_polling(poll_interval=3)

if __name__ == '__main__':
  main()