import requests
import base64
import datetime
from datetime import timedelta
from telegram import Bot
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackQueryHandler

GITHUB_TOKEN = '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'
TELEGRAM_BOT_TOKEN = '6363527340:AAGWoPQnlwXkO2RQvAQd0iGQHgprAH3a8_4'
REPO_OWNER = 'anang11042000'
REPO_NAME = 'vps'
FILE_PATH = 'izin'
BRANCH_NAME = 'main'

def start(update, context):
    update.message.reply_text('Bot is running! Use /addip to update the GitHub file.')

def edit_file(update, context):
    context.user_data['editing_stage'] = 'username'
    update.message.reply_text('Masukkan username.')

def handle_user_input(update, context):
    if 'editing_stage' in context.user_data:
        user_input = update.message.text

        if context.user_data['editing_stage'] == 'username':
            context.user_data['username'] = user_input
            update.message.reply_text('Masukkan IP VPS.')
            context.user_data['editing_stage'] = 'ip'
        elif context.user_data['editing_stage'] == 'ip':
            context.user_data['ip'] = user_input
            update.message.reply_text('Masukkan jumlah hari untuk ditambahkan.')
            context.user_data['editing_stage'] = 'exp_date_input'
        elif context.user_data['editing_stage'] == 'exp_date_input':
            try:
                # Ambil jumlah hari yang ditambahkan dari input pengguna
                days_to_add = int(user_input)

                # Hitung tanggal baru berdasarkan jumlah hari yang ditambahkan
                new_date = datetime.datetime.now() + timedelta(days=days_to_add)

                # Format ulang tanggal baru sesuai dengan 'TTTT-MM-DD'
                formatted_new_date = new_date.strftime('%Y-%m-%d')

                # Simpan tanggal expired yang sudah diformat
                context.user_data['exp_date'] = formatted_new_date
            except ValueError:
                update.message.reply_text('Error: Masukkan jumlah hari yang valid.')
                return

            github_api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get(github_api_url, headers=headers)
            data = response.json()

            current_content = base64.b64decode(data['content']).decode()
            new_message = f"### {context.user_data['username']} {context.user_data['exp_date']} {context.user_data['ip']}"
            new_content = f"{current_content}\n{new_message}"
            encoded_content = base64.b64encode(new_content.encode()).decode()

            update_data = {
                'message': 'Update file via Telegram bot',
                'content': encoded_content,
                'sha': data['sha'],
                'branch': BRANCH_NAME
            }

            response = requests.put(github_api_url, headers=headers, json=update_data)

            if response.status_code == 200:
                update.message.reply_text('Berhasil registrasi ip!, Silahkan ketik /addip untuk mendaftarkan ip lagi')
            else:
                update.message.reply_text(f'Failed to update file. Status code: {response.status_code}')

            del context.user_data['editing_stage']
            context.user_data.clear()
        else:
            update.message.reply_text('Error: Tahap pengeditan tidak dikenali. Harap mulai ulang proses.')

def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('addip', edit_file))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
