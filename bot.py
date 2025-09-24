# ================== bot.py ==================
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from config import BOT_TOKEN
from handlers import (
    start,
    category_selected,
    handle_model,
    summary,
    handle_summary_callback,
    CHOOSE_CATEGORY,
    ASK_MODEL,
    handle_model_selection,
    restart_search
)

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_CATEGORY: [CallbackQueryHandler(category_selected)],
            ASK_MODEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_model),
                CallbackQueryHandler(handle_model_selection, pattern="^select::")
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_message=False
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(restart_search, pattern="^restart$"))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CallbackQueryHandler(handle_summary_callback, pattern="^summary_"))

    logging.info("Bot started...")
    app.run_polling()
