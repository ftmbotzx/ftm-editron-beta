import logging
import os
import ffmpeg
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ftm import API_ID, API_HASH, BOT_TOKEN  # Importing credentials from ftm.py

# ✅ Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Client("FTM_Editron", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_PATH = "./downloads/"
video_queue = {}

# Ensure download directory exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

logger.info("🚀 Bot is starting...")

# 🚀 Custom Welcome Message
@app.on_message(filters.command("start"))
async def start(client, message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    logger.info(f"User {user_name} ({user_id}) started the bot.")

    welcome_text = f"""🚩 **जय श्री राम**  

ʜᴇʏ {user_name}, {user_id}  

ɪ ᴀᴍ ᴛʜᴇ ᴏꜰꜰɪᴄɪᴀʟ ʙᴏᴛ ᴏꜰ **FTM Editron BetaWave** 🎬  
ᴄʀᴇᴀᴛᴇᴅ ʙʏ **Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ** 🚀  
ᴜꜱᴇ ᴍᴇ ᴛᴏ ᴍᴇʀɢᴇ & ᴄᴏᴍᴘʀᴇss ᴠɪᴅᴇᴏꜱ ᴅɪʀᴇᴄᴛʟʏ ɪɴ Tᴇʟᴇɢʀᴀᴍ! 🚀  

🌿 **ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ:** [Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ](https://t.me/ftmdeveloperz)"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Merge Videos 🔗", callback_data="merge_now"),
         InlineKeyboardButton("Compress Video 📉", callback_data="compress_now")]
    ])

    await message.reply_text(welcome_text, reply_markup=buttons)

# 📥 Store Videos for Merging
@app.on_message(filters.video)
async def store_video(client, message):
    user_id = message.from_user.id
    if user_id not in video_queue:
        video_queue[user_id] = []
    
    file_path = await message.download(file_name=DOWNLOAD_PATH + message.video.file_name)

    if file_path:
        video_queue[user_id].append(file_path)
        logger.info(f"User {user_id} uploaded a video: {message.video.file_name}")
        await message.reply_text(f"✅ Video added! Total: {len(video_queue[user_id])}",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton("Merge Now 🔗", callback_data="merge_now"),
                                      InlineKeyboardButton("Clear Files ❌", callback_data="clear_files")]
                                 ]))
    else:
        await message.reply_text("❌ Download failed. Try again.")

# 🔗 Merge Videos with Progress Bar
@app.on_callback_query(filters.regex("merge_now"))
async def merge_videos(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in video_queue or len(video_queue[user_id]) < 2:
        return await callback_query.answer("❌ At least 2 videos needed!", show_alert=True)

    await callback_query.message.edit_text("⏳ Merging videos, please wait...")

    input_files = video_queue[user_id]
    list_file_path = os.path.join(DOWNLOAD_PATH, f"merge_list_{user_id}.txt")

    with open(list_file_path, "w") as f:
        for file in input_files:
            f.write(f"file '{file}'\n")

    output_file = os.path.join(DOWNLOAD_PATH, f"merged_{user_id}.mp4")

    merge_command = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file_path, "-c", "copy", output_file
    ]
    os.system(" ".join(merge_command))

    logger.info(f"User {user_id} merged {len(input_files)} videos.")
    await callback_query.message.reply_video(output_file)
    del video_queue[user_id]

# 📉 Compress Video with Progress Bar
@app.on_callback_query(filters.regex("compress_now"))
async def compress_video(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in video_queue or len(video_queue[user_id]) == 0:
        return await callback_query.answer("❌ No video found! Send a video first.", show_alert=True)

    await callback_query.message.edit_text("⏳ Compressing video, please wait...")

    input_file = video_queue[user_id][-1]
    output_file = os.path.join(DOWNLOAD_PATH, f"compressed_{user_id}.mp4")

    compress_command = [
        "ffmpeg", "-i", input_file,
        "-vcodec", "libx264", "-crf", "28", output_file
    ]
    os.system(" ".join(compress_command))

    logger.info(f"User {user_id} compressed video: {input_file}")
    await callback_query.message.reply_video(output_file)

# 🚀 Run the bot
if __name__ == "__main__":
    logger.info("✅ Bot is running!")
    app.run()
