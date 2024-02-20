from typing import Final
from telegram import Update, Bot
from telegram import InputMediaPhoto
from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, filters, MessageHandler, ContextTypes
from telegram.ext import Updater
import requests
import time

TOKEN: Final = "0000"
APIKEY: Final = '0000'
BOT_USERNAME: Final = "@nowplaying_sameerasw_bot"
APIURL: Final = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=S4m33r4&limit=1&api_key=';

# read telegram bot API and audioscrobbler API tokens from the tokens.txt file
try:
    with open('tokens.txt', 'r') as file:
        TOKEN = file.readline().strip()
        APIKEY = file.readline().strip()
        print(f'Token: {TOKEN}', f'API Key: {APIKEY}', sep='\n')
except:
    print('Error reading tokens.txt file')

FETCH_URL = f'{APIURL}{APIKEY}&format=json'
PLAYLIST = 'https://music.youtube.com/playlist?list=PLwPOyB_hI8FvpPFGHdHNEIc7kOowdfoRZ&si=Ih6b0Yh2nsFwpC_E'

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm the music bot who returns you what @sameera_s_w is listening to. Just type /nowplaying to get the current song.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just type /nowplaying to get the current song.")

async def auto_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if the command was a reply to a message, get the chat_id and message_id of the message to update or warn the user
    try:
        if update.message.reply_to_message:
            chat_id = update.message.chat.id
            message_id = update.message.reply_to_message.message_id - 1
            command_message_id = update.message.message_id
        else:
            await update.message.reply_text("Please reply to the message you want to update.")
            return
        # chat_id = '@tidwib'
        # message_id = 17028
        previous_song = ''
        bot = Bot(TOKEN)
        # delete the command message
        try:
            await bot.delete_message(chat_id, command_message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
            pass
        #update the message every 30 seconds
        await updating(update, context, chat_id, message_id, previous_song, bot)
    except Exception as e:
        print(f'Error: {e}')

async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the latest API data and return the song, also update the last sent message each 30 seconds with the new song using telegram-bot
    bot = Bot(TOKEN)
    while True:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
        now_playing_text = fetch_now_playing()

        # send the message as a photo with the album art and the song as a caption and add a button to open song info and another to open the playlist
        await bot.sendPhoto(chat_id, now_playing_text.split('|')[2], caption=now_playing_text.split('|')[0], parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Song info 🎵", url=now_playing_text.split('|')[1]),],[InlineKeyboardButton("Check out my Playlist ▶️", url=PLAYLIST),]]))

        previous_song = now_playing_text
        #update the message every 30 seconds
        await updating(update, context, chat_id, message_id, previous_song, bot)

async def updating(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str, message_id: str, previous_song: str, bot: Bot):
    while True:
            now_playing_text = fetch_now_playing()
            if now_playing_text != previous_song:
                
                # update the message as a photo with the album art and the song as a caption using editMessageMedia
                media = InputMediaPhoto(media=now_playing_text.split('|')[2], caption=now_playing_text.split('|')[0], parse_mode=ParseMode.HTML)

                try:
                    await bot.edit_message_media(chat_id=chat_id, message_id=message_id + 1, media=media, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Song info 🎵", url=now_playing_text.split('|')[1]),],[InlineKeyboardButton("Check out my Playlist ▶️", url=PLAYLIST),]]))
                    print("Message edited successfully!", now_playing_text.split('|')[0], ' in chat:', chat_id)
                except Exception as e:
                    print(f"Error editing message: {e}")
                    continue

                previous_song = now_playing_text
            time.sleep(10)

# responses
def handle_response(text: str) -> str:
    processed_text: str = text.lower()

    if 'hello' in processed_text:
        return "Hi there!"

    if 'how are you' in processed_text:
        return "I'm good, thank you!"

    return "I'm sorry, I'm not able to do that right now."

def fetch_now_playing():
    try:
        response = requests.get(FETCH_URL)
        data = response.json()
        track = data['recenttracks']['track'][0]
        artist = track['artist']['#text']
        album = track['album']['#text']
        image = track['image'][3]['#text']
        url = track['url']

        if image == '':
            image = 'https://raw.githubusercontent.com/sameerasw/music-bot/main/logo.jpg'

        return f'<b>@sameera_s_w</b> is listening to: <b>{track["name"]}</b> by <i>{artist}</i> on YouTube Music |{url}|{image}'
    except:
        return "Sorry, I can't get the current song right now. Please try again later.||"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    try:
        app = Application.builder().token(TOKEN).build()


        #commands
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("nowplaying", nowplaying_command))
        app.add_handler(CommandHandler("autoupdate", auto_update))
        
        #messages
        app.add_handler(MessageHandler(filters.TEXT, handle_message))
    except Exception as e:
        print(f'Error starting bot: {e}')

    #errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)





