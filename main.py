from typing import Final
from telegram import Update, Bot
from telegram import InputMediaPhoto
from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, filters, MessageHandler, ContextTypes
from telegram.ext import Updater
import requests
import time

# constants
REFRESH = 20  # Time interval for refreshing the song info
TOKEN: Final = "0000"  # Placeholder for Telegram Bot API token
APIKEY: Final = '0000'  # Placeholder for Audioscrobbler API key
BOT_USERNAME: Final = "@nowplaying_sameerasw_bot"  # Bot username
APIURL: Final = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=S4m33r4&limit=1&api_key='  # API URL for fetching recent tracks
WEBSITE: Final = 'https://t.me/nowplaying_sameerasw_bot/sameerasw'  # Website URL
old_img = 'https://raw.githubusercontent.com/sameerasw/music-bot/main/logo.jpg'  # Default image URL

# function that will log the passed text to the debug.log file
def log_file(text: str):
    with open('debug.log', 'a') as file:
        file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + text + '\n')

# this will save the last replied message id to the .data file so the bot can continue on restart.
def data_save(text: str, chat_id: str):
    with open('.data', 'w') as file:
        file.write(text + '\n' + chat_id)

# this will read the last replied message id from the .data file so the bot can continue on restart.
def data_read():
    try:
        with open('.data', 'r') as file:
            # return an array with the last_message_id and chat_id
            return file.read().splitlines()
    except:
        return None

# Read Telegram Bot API and Audioscrobbler API tokens from the tokens.txt file
try:
    with open('tokens.txt', 'r') as file:
        TOKEN = file.readline().strip()
        APIKEY = file.readline().strip()
        print(f'Token: {TOKEN}', f'API Key: {APIKEY}', sep='\n')
except Exception as e:
    print(f'Error reading tokens: {e}')
    log_file(f'Error reading tokens: {e}')
    # Ask for the tokens if the file is not found
    TOKEN = input('Enter your Telegram Bot API token: ')
    APIKEY = input('Enter your Audioscrobbler API key: ')

FETCH_URL = f'{APIURL}{APIKEY}&format=json'  # Complete URL for fetching recent tracks
PLAYLIST = 'https://music.youtube.com/playlist?list=PLwPOyB_hI8FvpPFGHdHNEIc7kOowdfoRZ&si=Ih6b0Yh2nsFwpC_E'  # Playlist URL

# Command to start the bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Hi! I'm the music bot who returns you what @sameera_s_w is listening to. Just type /nowplaying to get the current song.")
    except Exception as e:
        print(f'Error in start_command: {e}')
        log_file(f'Error in start_command: {e}')

# Command to provide help information
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Just type /nowplaying to get the current song or reply to an already sent message with /autoupdate to get the current song updated every 10 seconds.")
    except Exception as e:
        print(f'Error in help_command: {e}')
        log_file(f'Error in help_command: {e}')

# Command to automatically update the song info
async def auto_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.reply_to_message:
            chat_id = update.message.chat.id
            message_id = update.message.reply_to_message.message_id - 1
            command_message_id = update.message.message_id
        else:
            await update.message.reply_text("Please reply to the message you want to update.")
            return
        previous_song = ''
        bot = Bot(TOKEN)
        # Delete the command message
        try:
            await bot.delete_message(chat_id, command_message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
            log_file("Error deleting message: " + str(e))
            pass
        # Update the message every 30 seconds
        await updating(update, context, chat_id, message_id, previous_song, bot)
    except Exception as e:
        print(f'Error in auto_update: {e}')
        log_file('Error in auto_update: ' + str(e))

# Command to get the currently playing song
async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bot = Bot(TOKEN)
        while True:
            chat_id = update.message.chat.id
            message_id = update.message.message_id
            now_playing_text = fetch_now_playing()


            # Save the last replied message id and the chat id to the .data file
            data_save(str(message_id), str(chat_id))

            # Send the message as a photo with the album art and the song as a caption
            await bot.sendPhoto(chat_id, now_playing_text.split('|')[2], caption=now_playing_text.split('|')[0], parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Song info 🎵", url=now_playing_text.split('|')[1]),],[InlineKeyboardButton("Check out my Playlist ▶️", url=PLAYLIST),],[InlineKeyboardButton("Visit my Website 🌐", url=WEBSITE),]]))

            previous_song = now_playing_text
            # Update the message every 30 seconds
            await updating(update, context, chat_id, message_id, previous_song, bot)


    except Exception as e:
        print(f'Error in nowplaying_command: {e}')
        log_file('Error in nowplaying_command: ' + str(e))

# Function to update the song info
async def updating(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str, message_id: str, previous_song: str, bot: Bot):
    while True:
        try:
            now_playing_text = fetch_now_playing()
            if now_playing_text != previous_song:
                # Update the message as a photo with the album art and the song as a caption
                media = InputMediaPhoto(media=now_playing_text.split('|')[2], caption=now_playing_text.split('|')[0], parse_mode=ParseMode.HTML)

                try:
                    await bot.edit_message_media(chat_id=chat_id, message_id=message_id + 1, media=media, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Song info 🎵", url=now_playing_text.split('|')[1]),],[InlineKeyboardButton("Check out my Playlist ▶️", url=PLAYLIST),],[InlineKeyboardButton("Visit my Website 🌐", url=WEBSITE),]]))
                    print("Message edited successfully!", now_playing_text.split('|')[0], ' in chat:', chat_id)
                    log_file("Message edited successfully! " + now_playing_text.split('|')[0] + ' in chat: ' + str(chat_id))
                except Exception as e:
                    print(f"Error editing message: {e}")
                    log_file("Error editing message: " + str(e))
                    continue

                previous_song = now_playing_text
            time.sleep(REFRESH)
        except Exception as e:
            print(f'Error in updating: {e}')
            log_file('Error in updating: ' + str(e))

# Function to handle responses based on user input
def handle_response(text: str) -> str:
    try:
        processed_text: str = text.lower()

        if 'hello' in processed_text:
            return "Hi there!"

        if 'how are you' in processed_text:
            return "I'm good, thank you!"

        return "I'm sorry, I'm not able to do that right now."
    except Exception as e:
        print(f'Error in handle_response: {e}')
        log_file('Error in handle_response: ' + str(e))
        return "An error occurred while processing your request."

# Function to fetch the currently playing song from the API
def fetch_now_playing():
    try:
        old_img = 'https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png'
        response = requests.get(FETCH_URL)
        data = response.json()
        track = data['recenttracks']['track'][0]
        artist = track['artist']['#text']
        album = track['album']['#text']
        image = track['image'][3]['#text']
        url = track['url']

        if image == '' or image == old_img:
            image = 'https://raw.githubusercontent.com/sameerasw/music-bot/main/logo.jpg'

        return f'<b>@sameera_s_w</b> is listening to: <b>{track["name"]}</b> by <i>{artist}</i> on YouTube Music |{url}|{image}'
    except Exception as e:
        print(f'Error in fetch_now_playing: {e}')
        log_file('Error in fetch_now_playing: ' + str(e))
        return "Sorry, I can't get the current song right now. Please try again later.||"

# Function to handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_type: str = update.message.chat.type
        text: str = update.message.text

        print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
        log_file("User (" + str(update.message.chat.id) + ") in " + message_type + ": " + text)

        if message_type == 'group' or message_type == 'supergroup':
            if BOT_USERNAME in text:
                new_text = text.replace(BOT_USERNAME, '').strip()
                response: str = handle_response(new_text)
            else:
                return
        else:
            response: str = handle_response(text)

        print('Bot:', response)
        await update.message.reply_text(response)
    except Exception as e:
        print(f'Error in handle_message: {e}')
        log_file('Error in handle_message: ' + str(e))

# Function to handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print(f'Update {update} caused error {context.error}')
        log_file("Update " + str(update) + " caused error " + str(context.error))
    except Exception as e:
        print(f'Error in error handler: {e}')
        log_file('Error in error handler: ' + str(e))

# Main function to start the bot
if __name__ == '__main__':
    print('\nStarting bot...')
    log_file('Starting bot...\n')
    try:
        app = Application.builder().token(TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("nowplaying", nowplaying_command))
        app.add_handler(CommandHandler("autoupdate", auto_update))

        # Add message handler
        app.add_handler(MessageHandler(filters.TEXT, handle_message))


        #if the bot is restarted, it will continue from the last replied message, if there isn't any, it will start from the beginning
        last_data = data_read()
        
        if last_data:
            try:
                # get the last_message_id and chat_id from the .data file as an array
                last_message_id = last_data[0]
                chat_id = last_data[1]
                app.run_polling(poll_interval=7, last_message_id=int(last_message_id), chat_id=int(chat_id))
            except Exception as e:
                print(f'Error in run_polling: {e}')
                log_file('Error in run_polling: ' + str(e))
                
    except Exception as e:
        print(f'Error starting bot: {e}')
        log_file('Error starting bot: ' + str(e))

    # Add error handler
    app.add_error_handler(error)

    print('Polling...')
    log_file('Polling...')


    try:
        app.run_polling(poll_interval=7)
    except Exception as e:
        print(f'Error in run_polling: {e}')
        log_file('Error in run_polling: ' + str(e))

    print('Bot stopped.')
    log_file('Bot stopped.')