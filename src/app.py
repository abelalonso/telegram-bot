import os
import json
from telegram import (
  Bot,
  Update
)
from telegram.ext import (
  Dispatcher,
  MessageHandler,
  Filters,
  CallbackContext
)


def echo(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(update.message.text)


def handler(event, context):
  print(event)
  bot = Bot(os.environ["BOT_TOKEN"])
  dispatcher = Dispatcher(bot, None, workers=0)
  dispatcher.add_handler(MessageHandler(Filters.text, echo))
  dispatcher.process_update(Update.de_json(json.loads(event["body"]), bot))