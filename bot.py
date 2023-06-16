import os
import yaml
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# load yaml config
with open("config.yml", "r") as f:
  config_yaml = yaml.safe_load(f)
telegram_token = config_yaml["telegram_token"]
bot_username = config_yaml["bot_username"]
authorized_users = config_yaml["authorized_users"]

# Directory to save received pictures and messages
save_directory = "received-docs"
if not os.path.exists(save_directory):
  os.makedirs(save_directory)

# Commands


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message = """Welcome, adventurer! Fame and fortune avait! \n\n
    To save document add it without compression and write it's name in format: \n
    Name_of_owner. Name_of_document \n\n
    To get it back write: \n
    Give (or Дай) Name_of_owner Name_of_document"""

  await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message = "Now we can:\n\n"
  possibilities = [
      "📸 Save your dos and photos",
      "📋 Organize your docs by names",
      "✉️ Keep a record of your thoughts",
  ]

  message += "\n".join(possibilities[:3])
  await update.message.reply_text(message)


# Saves document to this computer


async def save_doc(file_name, update: Update, context: ContextTypes.DEFAULT_TYPE):
  folder_name = file_name.split(".")[0].strip()

  subfolder_path = os.path.join(save_directory, folder_name)
  if not os.path.exists(subfolder_path):
    os.makedirs(subfolder_path)

  file_path = os.path.join(subfolder_path, file_name)

  if os.path.exists(file_path):
    await update.message.reply_text("File already exists. Should it be replaced?")
    await context.bot.send_document(
        chat_id=update.message.chat_id, document=file_path
    )
    context.user_data["conflict_path"] = file_path
    return

  file = await context.bot.get_file(context.user_data["doc_id"])
  await file.download_to_drive(file_path)
  del context.user_data["doc_id"]
  await update.message.reply_text(f"{file_name} saved.")
  return


async def handle_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.message.from_user.id

  if user_id in authorized_users:
    if update.message.photo:
      context.user_data["doc_id"] = update.message.photo[-1].file_id
      if update.message.caption:
        doc_name = update.message.caption.strip() + '.jpg'
        await save_doc(doc_name, update, context)
        return
      else:
        context.user_data["doc_type"] = '.jpg'
        await update.message.reply_text("Write file name in format: \n Owner. File name")
        return

    if update.message.document:
      supported_formats = {
          "image/jpeg": ".jpg",
          "application/pdf": ".pdf",
          "application/msword": ".doc",
      }
      file_type = update.message.document.mime_type
      if file_type in supported_formats:
        context.user_data["doc_id"] = update.message.document.file_id
        if update.message.caption:
          doc_name = (
              update.message.caption.strip(
              ) + supported_formats[file_type]
          )
          await save_doc(doc_name, update, context)
        else:
          context.user_data["doc_type"] = supported_formats[file_type]
          await update.message.reply_text("Write file name in format: \n Owner - File name")
          return
      else:
        await update.message.reply_text("Unsupported type")
        return
    else:
      await update.message.reply_text("Unsupported type")
      return

def save_message(text: str, user_id: str, bot=False):
  if user_id in authorized_users:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_path = os.path.join(save_directory, f"{user_id}.txt")
    if bot == False:
      with open(save_path, "a") as file:
        file.write(f"{now} : {text}" + "\n")
    else:
      with open(save_path, "a") as file:
        file.write(f"{now} : Bot: {text}" + "\n")

# Responses

def handle_response(text: str) -> str:
  proccesed: str = text.lower()
  if "save" in proccesed:
    return "Upload it here and write the name under photo"
  if "give" or "дай" in proccesed:
    return "Wait a bit, it will work later"
  else:
    return


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_type: str = update.message.chat.type
  user_id: str = update.message.from_user.id
  text: str = update.message.text

  if "doc_id" in context.user_data:
    if "conflict_path" in context.user_data:
      if text.lower() == "yes" or text.lower() == "да":
        file = await context.bot.get_file(context.user_data["doc_id"])
        await file.download_to_drive(context.user_data["conflict_path"])
        del context.user_data["doc_id"]
        del context.user_data["conflict_path"]
        await update.message.reply_text("Done")
        return
      else:
        del context.user_data["conflict_path"]
        await update.message.reply_text("Enter another name")
        return
    await save_doc(text + context.user_data["doc_type"], update, context)
    del context.user_data["doc_type"]
    return

  save_message(text, user_id)

  if chat_type == "group":
    if bot_username in text:
      new_text: str = text.replace(bot_username, "").strip()
      response: str = handle_response(new_text)
    else:
      return
  else:
    response: str = handle_response(text)
    if response != None:
      save_message(response, user_id, True)
      await update.message.reply_text(response)
      return


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
  print(f"Update {update} \n err: {context.error}")


def main():
  print('bot is running')
  app = Application.builder().token(telegram_token).build()

  # Commands
  app.add_handler(CommandHandler("start", start_command))
  app.add_handler(CommandHandler("help", help_command))

  # Messages
  app.add_handler(MessageHandler(filters.ATTACHMENT, handle_doc))
  app.add_handler(MessageHandler(filters.TEXT, handle_message))

  # Error
  app.add_error_handler(error)

  # Polls the bot
  app.run_polling(poll_interval=3)


if __name__ == "__main__":
  main()
