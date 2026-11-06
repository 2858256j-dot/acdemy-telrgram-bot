import os
import sqlite3
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

COURSE, NAME, PHONE = range(3)

def save_student(name, phone, course):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            course TEXT
        )
    """)

    cursor.execute(
        "INSERT INTO students (name, phone, course) VALUES (?, ?, ?)",
        (name, phone, course)
    )

    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Python", "Web Development"],
        ["Graphic Design", "Digital Marketing"]
    ]

    await update.message.reply_text(
        "أهلاً بيك في أكاديمية المستقبل 🎓\n"
        "اختار الكورس اللي حابب تسجل فيه:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

    return COURSE


async def choose_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["course"] = update.message.text

    await update.message.reply_text(
        "تمام! اكتب اسمك بالكامل:"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[KeyboardButton(
        "مشاركة رقم الهاتف 📱",
        request_contact=True
    )]]

    await update.message.reply_text(
        "اضغط على الزر لمشاركة رقم هاتفك:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.contact:
        await update.message.reply_text(
            "من فضلك استخدم زر مشاركة رقم الهاتف."
        )
        return PHONE

    phone = update.message.contact.phone_number
    name = context.user_data["name"]
    course = context.user_data["course"]

    save_student(name, phone, course)

    await update.message.reply_text(
        "تم تسجيل بياناتك بنجاح! ✅\n\n"
        f"الاسم: {name}\n"
        f"الكورس: {course}\n\n"
        "هنراجع طلبك ونتواصل معاك قريباً ❤️",
        reply_markup=ReplyKeyboardMarkup(
            [["/start"]],
            resize_keyboard=True
        )
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء التسجيل.")
    return ConversationHandler.END


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COURSE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_course)
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)
            ],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conversation)

    print("Academy bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
