import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

rounds = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✈️ Sam Aviator Helper\n\n"
        "/add 1.45 - Record a round\n"
        "/history - Recent rounds\n"
        "/stats - Statistics\n"
        "/alert - Statistical report\n\n"
        "Note: Next multiplier cannot be reliably predicted."
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = float(context.args[0])
        if not 1 <= value <= 100000:
            raise ValueError
        chat = update.effective_chat.id
        rounds.setdefault(chat, []).append(value)
        rounds[chat] = rounds[chat][-100:]
        await update.message.reply_text(f"Saved: {value:.2f}x")
    except (ValueError, IndexError):
        await update.message.reply_text("Example: /add 1.45")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = rounds.get(update.effective_chat.id, [])
    if not data:
        await update.message.reply_text("No rounds yet. Use /add 1.45")
        return
    await update.message.reply_text(
        "Recent rounds:\n" + "\n".join(f"{x:.2f}x" for x in data[-20:])
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = rounds.get(update.effective_chat.id, [])
    if not data:
        await update.message.reply_text("Record rounds first: /add 1.45")
        return
    low = sum(x < 2 for x in data)
    avg = sum(data) / len(data)
    await update.message.reply_text(
        f"Rounds: {len(data)}\n"
        f"Average: {avg:.2f}x\n"
        f"Below 2x: {low} ({low/len(data)*100:.1f}%)\n"
        f"2x or above: {len(data)-low}\n\n"
        "Past results cannot reliably predict the next round."
    )

async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await stats(update, context)

app = ApplicationBuilder().token(
    os.environ["TELEGRAM_BOT_TOKEN"]
).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("history", history))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("alert", alert))

app.run_polling()
