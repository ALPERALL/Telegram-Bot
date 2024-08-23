import logging
import requests
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Bot token'ınızı buraya ekleyin
my_bot_token = '7196669683:AAH_ID98UlbkP_HUExE6dzmbbUJF1P2twjQ'

# URL ve istek başlıklarını ayarlayın
CHECK_URL = 'https://checker.visatk.com/ccn1/alien07.php'
HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-GB,en;q=0.9,tr-TR;q=0.8,tr;q=0.7,en-US;q=0.6',
    'content-length': '57',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': '__gads=ID=c1d904dc8d091df3-225fb18247e00013:T=1691166839:RT=1691166839:S=ALNI_MYoYYmWJaRMNOYcK_YijqwKW6AQ0g; __gpi=UID=00000c77b2c6e3ba:T=1691166839:RT=1691166839:S=ALNI_ManGmC_qU8zuQyNMQbNSw5J3kMHFA; PHPSESSID=q2ep2h2g5977bn39qbtv0uekf3; FCNEC=%5B%5B%22AKsRol-CV7xbsBLpSARmDYu9Tvuv9suohxhteHPFOy-Prutb5qKe6hT6zcqP0c0bkkONI7DzfjVUbl8Ag8PEN_g0vBIaYvJ65O13RheCfyhhQXyY1fOClvRC3WxgTL9xRaMb25wcHosNEyq9NX_wpWwoE6hCRy7ZSQ%3D%3D%22%5D%2Cnull%2C%5B%5D%5D',
    'origin': 'https://checker.visatk.com',
    'referer': 'https://checker.visatk.com/ccn1/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 9; SM-J701F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

# Logging ayarlama
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot başlatıldığında veya /start komutu gönderildiğinde çağrılır."""
    user = update.effective_user
    await update.message.reply_text(
        f"Merhaba {user.mention_html()}! Kart kontrolü yapmak için lütfen /check komutunu kullanın.",
        parse_mode='HTML'
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kullanıcı /check komutu gönderdiğinde çağrılır."""
    await update.message.reply_text('Lütfen Kart Dosyasını Gönderiniz.')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kullanıcı bir dosya gönderdiğinde çağrılır."""
    document = update.message.document
    if not document:
        await update.message.reply_text("Lütfen bir dosya gönderin.")
        return

    file = await context.bot.get_file(document.file_id)
    visa_list = (await file.download_as_bytearray()).decode('utf-8').splitlines()

    for visa in visa_list:
        data = {
            'ajax': '1',
            'do': 'check',
            'cclist': visa
        }

        response = requests.post(CHECK_URL, headers=HEADERS, data=data).text
        
        # Yalnızca aktif kartlar için yanıt gönder
        if 'Live' in response:
            await update.message.reply_text(f'AKTİF KART ✅ | {visa}')

def main() -> None:
    """Botun ana fonksiyonu. Güncelleyici ve işleyicileri başlatır."""
    application = Application.builder().token(my_bot_token).build()

    # Komut işleyicilerini ekle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Botu çalıştır
    application.run_polling()

if __name__ == "__main__":
    main()
