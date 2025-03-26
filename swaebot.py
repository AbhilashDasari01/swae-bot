import discord
import google.generativeai as genai
import aiohttp
import asyncio
import random
import os  # ✅ Import OS to use environment variables

from dotenv import load_dotenv
load_dotenv("swaebot.env")  # ✅ Explicitly load swaebot.env

# ✅ Get tokens securely from environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"

# ✅ Configure Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  

# ✅ Setup bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Allow bot to read message content
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

MAX_DISCORD_MESSAGE_LENGTH = 2000  # ✅ Discord message character limit

# ✅ Bot Ready Event
@client.event
async def on_ready():
    await tree.sync()
    print(f"🤖 {client.user} is online!")

# ✅ /swaebot Command (Funny Greeting)
@tree.command(name="swaebot", description="Get a funny greeting from SwaeBot!")
async def swaebot_command(interaction: discord.Interaction):
    greetings = [
        "Yo! I'm SwaeBot, your AI overlord! Bow before me! 😎",
        "Beep boop! I'm here to entertain and chat. What’s up? 🚀",
        "Error 404: Chill Mode Not Found. Let's chat! 😂",
        "Greetings, human! I bring memes and wisdom. 🔥"
    ]
    await interaction.response.send_message(random.choice(greetings))

# ✅ /chat Command (AI Chat with Gemini 1.5 Flash)
@tree.command(name="chat", description="Talk to SwaeBot using AI!")
async def chat_command(interaction: discord.Interaction, message: str):
    await interaction.response.defer()  # Acknowledge the command first

    try:
        response = model.generate_content([message])
        reply = response.text if response.text else "Oops! No response from AI. 😢"

        # ✅ Truncate long messages to fit Discord’s limit
        if len(reply) > MAX_DISCORD_MESSAGE_LENGTH:
            reply = reply[:MAX_DISCORD_MESSAGE_LENGTH - 10] + "..."

    except Exception as e:
        reply = f"⚠️ AI Error: {e}"

    await interaction.followup.send(reply)

# ✅ Respond when the bot is mentioned (@SwaeBot)
@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore the bot's own messages

    if client.user in message.mentions:  # If bot is mentioned
        try:
            user_prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
            if not user_prompt:
                await message.reply("Hey! How can I help? 😊")
                return

            response = model.generate_content([user_prompt])
            reply = response.text if response.text else "Oops! No response from AI. 😢"

            # ✅ Truncate response if too long
            if len(reply) > MAX_DISCORD_MESSAGE_LENGTH:
                reply = reply[:MAX_DISCORD_MESSAGE_LENGTH - 10] + "..."

            await message.reply(reply)

        except Exception as e:
            await message.reply(f"⚠️ AI Error: {e}")

# ✅ Run the bot
client.run(DISCORD_BOT_TOKEN)