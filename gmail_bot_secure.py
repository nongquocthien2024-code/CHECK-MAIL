import os
import logging
import asyncio
from cryptography.fernet import Fernet
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === CẤU HÌNH BẢO MẬT ===
FERNET_KEY = os.getenv("FERNET_KEY") or Fernet.generate_key().decode()
fernet = Fernet(FERNET_KEY)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_USER_IDS", "").split(",")  # ví dụ: "12345678,98765432"

logging.basicConfig(level=logging.INFO)

# === CÁC LỚP BẢO MẬT ===
def encrypt_text(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMIN_IDS

# === HÀM CHÍNH CỦA BOT ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Xin chào! Đây là bot kiểm tra Gmail và hỗ trợ phân tích thông tin an toàn.\n"
        "Gõ /check tên_gmail để kiểm tra.\n"
        "Ví dụ: /check nguyenvana"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Hãy nhập tên Gmail cần kiểm tra. Ví dụ: /check nguyenvana")
        return

    name = context.args[0]
    fake_gmail = f"{name.lower()}@gmail.com"

    # Giả lập kết quả kiểm tra — thực tế có thể mở rộng dùng API phân tích AI
    result = f"Gmail `{fake_gmail}` có thể đã tồn tại hoặc được đăng ký trước năm 2025."
    encrypted = encrypt_text(result)

    await update.message.reply_text(
        f"🔍 Kết quả kiểm tra (bảo mật):\n{encrypted}\n\n"
        "🧩 Gõ /decode <chuỗi> để giải mã (chỉ admin)."
    )

async def decode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 Bạn không có quyền dùng lệnh này.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("⚙️ Nhập chuỗi cần giải mã sau lệnh /decode")
        return

    token = context.args[0]
    try:
        decoded = decrypt_text(token)
        await update.message.reply_text(f"🔓 Giải mã thành công:\n{decoded}")
    except Exception:
        await update.message.reply_text("❌ Chuỗi không hợp lệ hoặc đã bị thay đổi.")

# === CHẠY BOT ===
async def main():
    if not BOT_TOKEN:
        print("⚠️ Thiếu TELEGRAM_BOT_TOKEN trong biến môi trường!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("decode", decode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    print("✅ Bot đã khởi động thành công...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
