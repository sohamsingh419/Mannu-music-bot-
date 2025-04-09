import asyncio
import os
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream, AudioPiped
import yt_dlp
import ffmpeg

# पर्यावरण चर से क्रेडेंशियल प्राप्त करें
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if API_ID == 0 or not API_HASH or not BOT_TOKEN:
    print("कृपया API_ID, API_HASH और BOT_TOKEN पर्यावरण चर सेट करें।")
    exit()

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

async def download_audio(url):
    ydl_opts = {'format': 'bestaudio/best'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Audio')
        return audio_url, title
    except Exception as e:
        print(f"ऑडियो डाउनलोड करने में त्रुटि: {e}")
        return None, None

@app.on_message(filters.command("join") & filters.group)
async def join_voice_chat(client, message):
    try:
        chat_id = message.chat.id
        await call.join_group_call(
            chat_id,
            stream=MediaStream(
                AudioPiped("https://github.com/pytgcalls/example-files/raw/main/long.mp3") # एक डिफ़ॉल्ट ऑडियो स्ट्रीम
            )
        )
        await message.reply_text("वॉयस चैट में शामिल हो गया!")
    except Exception as e:
        await message.reply_text(f"वॉयस चैट में शामिल होने में विफल: {e}")

@app.on_message(filters.command("play") & filters.group)
async def play_song(client, message):
    if len(message.command) < 2:
        await message.reply_text("कृपया गाने का URL प्रदान करें।")
        return

    query = message.command[1]
    audio_url, title = await download_audio(query)
    if audio_url:
        try:
            chat_id = message.chat.id
            await call.change_stream(
                chat_id,
                stream=MediaStream(AudioPiped(audio_url))
            )
            await message.reply_text(f"अब बज रहा है: {title}")
        except Exception as e:
            await message.reply_text(f"गाना चलाने में विफल: {e}")
    else:
        await message.reply_text("ऑडियो डाउनलोड करने में विफल।")

@app.on_message(filters.command("stop") & filters.group)
async def stop_song(client, message):
    try:
        chat_id = message.chat.id
        await call.leave_group_call(chat_id)
        await message.reply_text("गाना बंद कर दिया!")
    except Exception as e:
        await message.reply_text(f"गाना बंद करने में विफल: {e}")

@app.on_message(filters.command("leave") & filters.group)
async def leave_voice_chat(client, message):
    try:
        chat_id = message.chat.id
        await call.leave_group_call(chat_id)
        await message.reply_text("वॉयस चैट से हट गया!")
    except Exception as e:
        await message.reply_text(f"वॉयस चैट से हटने में विफल: {e}")

async def main():
    await app.start()
    await call.start()
    print("बॉट शुरू हो गया!")
    await idle()
    await call.stop()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
