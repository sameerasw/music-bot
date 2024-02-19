# 6809277533:AAG_vo_f5bgK8fLo7vkmkitrNl4D34PI7uA

from typing import Final
from telegram import Update, Bot
from telegram import InputMediaPhoto
# import telepot
from telegram.ext import Application, CommandHandler, filters, MessageHandler, ContextTypes
from telegram.ext import Updater
import requests
import time

TOKEN: Final = "6809277533:AAG_vo_f5bgK8fLo7vkmkitrNl4D34PI7uA"
BOT_USERNAME: Final = "@nowplaying_sameerasw_bot"
APIURL: Final = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=S4m33r4&limit=1&api_key=';
APIKEY: Final = 'd14224bbdbf51e2b2445f81731bedc57'
FETCH_URL = f'{APIURL}{APIKEY}&format=json'

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm the music bot who returns you what @sameera_s_w is listening to. Just type /nowplaying to get the current song.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just type /nowplaying to get the current song.")

async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the latest API data and return the song, also update the last sent message each 30 seconds with the new song using telegram-bot
    bot = Bot(TOKEN)
    while True:
        chat_id = update.message.chat.id
        message_id = update.message.message_id

        now_playing_text = fetch_now_playing()
        # extract the url from the message
        song_url = now_playing_text.split('|')[1]
        # extract the album art from the message
        album_art = now_playing_text.split('|')[2]
        caption_text = formatted_text(now_playing_text.split('|')[0])

        # send the message as a photo with the album art and the song as a caption
        await bot.sendPhoto(chat_id, album_art, caption=caption_text)

        previous_song = now_playing_text

        #update the message every 30 seconds
        while True:
            now_playing_text = fetch_now_playing()
            if now_playing_text != previous_song:
                song_url = now_playing_text.split('|')[1]
                album_art = now_playing_text.split('|')[2]
                
                # update the message as a photo with the album art and the song as a caption using editMessageMedia
                media = InputMediaPhoto(media=album_art, caption=now_playing_text.split('|')[0])

                try:
                    await bot.edit_message_media(chat_id=chat_id, message_id=message_id + 1, media=media)
                    print("Message edited successfully!")
                except Exception as e:
                    print(f"Error editing message: {e}")

                previous_song = now_playing_text
            time.sleep(30)


# responses
def handle_response(text: str) -> str:
    processed_text: str = text.lower()

    if 'hello' in processed_text:
        return "Hi there!"

    if 'how are you' in processed_text:
        return "I'm good, thank you!"

    return "I'm sorry, I'm not able to do that right now."

def formatted_text(text: str) -> str:
    return "@sameera_s_w is now listening to: " + text.split('*')[0] + " by " + text.split('*')[2]

def fetch_now_playing():
    try:
        response = requests.get(FETCH_URL)
        data = response.json()
        track = data['recenttracks']['track'][0]
        artist = track['artist']['#text']
        album = track['album']['#text']
        image = track['image'][3]['#text']
        url = track['url']
        return f'{track["name"]}* by *{artist} |{url}|{image}'
    except:
        return "Sorry, I can't get the current song right now. Please try again later."


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
    app = Application.builder().token(TOKEN).build()

    #commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("nowplaying", nowplaying_command))
    
    #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)





