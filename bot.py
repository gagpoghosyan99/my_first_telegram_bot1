from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, InlineQueryHandler,
    ContextTypes, filters
)
import math
import uuid
import re

TOKEN = '7618815581:AAFzwRwZnajzJNjT2KrNgoMcihlmkH3iRMY'

# Helper to convert % to proper division
def convert_percent(expr: str) -> str:
    tokens = re.findall(r'\d+\.?\d*%|[\d.]+|[+/*()-]', expr)
    output = []
    eval_stack = []

    for token in tokens:
        if '%' in token:
            number = float(token.replace('%', ''))
            try:
                prev_expr = ''.join(eval_stack)
                prev_value = eval(prev_expr, {"builtins": {}}, {})
                percent_value = f"({prev_value} * {number} / 100)"
                output.append(percent_value)
                eval_stack = [percent_value]
            except:
                output.append(f"({number} / 100)")
                eval_stack = [f"({number} / 100)"]
        else:
            output.append(token)
            if token.strip() not in "+-*/()":
                eval_stack.append(token)

    return ''.join(output)
# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ողջույն {update.effective_user.first_name}! Ես քո բոտն եմ 🤖")
    await update.message.reply_text("Պատրաստ եմ կատարել քեզ համար մաթեմատիկական գործողություններ։")

# Message handler
async def handle_math_expression(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expression = update.message.text
    expression = convert_percent(expression)

    try:
        if not all(char in "0123456789+-*/(). % " for char in expression):
            raise ValueError("Invalid characters detected.")

        result = eval(expression, {"builtins": {}}, {})
        await update.message.reply_text(f"Արդյունք: {result}")
    except ZeroDivisionError:
        await update.message.reply_text("Սխալ՝ բաժանում զրոյի վրա։")
    except Exception:
        await update.message.reply_text("Սխալ՝ անվավեր արտահայտություն։")

# Inline query handler
async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    query = convert_percent(query)

    results = []

    if re.fullmatch(r"[0-9+\-*/(). %]+", query):
        try:
            result = eval(query, {"builtins": {}}, {})
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"{query} = {result}",
                    input_message_content=InputTextMessageContent(f"✅ {query} = {result}")
                )
            )
        except Exception:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="⚠️ Սխալ արտահայտություն",
                    input_message_content=InputTextMessageContent("❌ Սխալ արտահայտություն")
                )
            )
    elif query:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="⚠️ Անվավեր նշաններ",
                input_message_content=InputTextMessageContent("❌ Խնդրում եմ մուտքագրել ճիշտ մաթեմատիկական արտահայտություն։")
            )
        )

    await update.inline_query.answer(results, cache_time=0)

# Run the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_math_expression))
    app.add_handler(InlineQueryHandler(inline_query_handler))

    print("🤖 Bot is running with inline support and percent handling...")
    app.run_polling()