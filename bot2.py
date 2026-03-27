from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ChatJoinRequestHandler,
    CallbackQueryHandler, ContextTypes,
    MessageHandler, CommandHandler, filters
)

# ===== Bot Token =====
BOT_TOKEN = "8723296682:AAFhkJL-ywQ2KBHxRXwZoCgaHMeWw8jbRQQ"

# ===== 管理員ID =====
ADMIN_IDS = [5494623381,7077341523]

# ===== 儲存UID =====
user_codes = {}


# ===== 安全發送（不會炸）=====
async def safe_send(bot, chat_id, text, reply_markup=None):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"[發送失敗] chat_id={chat_id}:", e)


# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_send(
        context.bot,
        update.effective_chat.id,
        "👉 請輸入8位數 Bingx UID"
    )


# ===== 接收UID =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text.isdigit() and len(text) == 8:
        user_codes[user_id] = text

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "👉 點我申請加入24H高勝率諧波訊號",
                url="https://t.me/+6ovAYV6HAYRlNmVl"
            )]
        ])

        await safe_send(
            context.bot,
            update.effective_chat.id,
            "✅ 已記錄UID，請點下方按鈕申請加入",
            reply_markup=keyboard
        )
    else:
        await safe_send(
            context.bot,
            update.effective_chat.id,
            "❌ 請輸入8位數 Bingx UID"
        )


# ===== 有人申請加入 =====
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    user = req.from_user

    code = user_codes.get(user.id, "❌ 未填寫")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ 批准",
                callback_data=f"approve_{user.id}_{req.chat.id}"
            ),
            InlineKeyboardButton(
                "❌ 拒絕",
                callback_data=f"reject_{user.id}_{req.chat.id}"
            )
        ]
    ])

    msg = f"""🔔 {user.first_name} 申請加入

ID: {user.id}
UID: {code}
"""

    if code == "❌ 未填寫":
        msg += "\n⚠️ 此人未填UID！"

    # 👉 發給管理員（用安全發送）
    for admin_id in ADMIN_IDS:
        await safe_send(context.bot, admin_id, msg, keyboard)


# ===== 按鈕處理 =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])
    chat_id = int(data[2])

    if action == "approve":
        await context.bot.approve_chat_join_request(chat_id, user_id)
        await query.edit_message_text(query.message.text + "\n\n✅ 已批准")

    elif action == "reject":
        await context.bot.decline_chat_join_request(chat_id, user_id)
        await query.edit_message_text(query.message.text + "\n\n❌ 已拒絕")


# ===== 主程式 =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot 啟動成功")
    app.run_polling()


if __name__ == "__main__":
    main()
