async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the latest API data and return the song, also update the last sent message each 30 seconds with the new song using telepot
    bot = telepot.Bot(TOKEN)
    chat_id = update.message.chat.id
    message_id = update.message.message_id

    now_playing_text = fetch_now_playing()
    # extract the url from the message
    song_url = now_playing_text.split('|')[1]
    # extract the album art from the message
    album_art = now_playing_text.split('|')[2]

    # send the message as a photo with the album art and the song as a caption
    bot.sendPhoto(chat_id, album_art, caption=now_playing_text.split('|')[0])

    previous_song = now_playing_text

    #update the message every 30 seconds
    while True:
        now_playing_text = fetch_now_playing()
        if now_playing_text != previous_song:
            song_url = now_playing_text.split('|')[1]
            album_art = now_playing_text.split('|')[2]
            
            # update the message as a photo with the album art and the song as a caption
            bot.editMessageCaption((chat_id, message_id+1), caption=now_playing_text.split('|')[0])

            previous_song = now_playing_text
        time.sleep(10)