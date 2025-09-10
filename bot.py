import discord
import json
from discord.ext import commands
from discord.ext import tasks
import aiohttp

from flask import Flask, request, jsonify
import threading
from datetime import datetime
from flask_cors import CORS
import re
import asyncio
from dotenv import load_dotenv
import os
import io
import zoneinfo
import random

load_dotenv()
#note
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GENERAL_PAIRINGS_CHANNEL_ID = 1359343581705539726
TNF_PARINGS_CHANNEL_ID = 1119468407084023930
TNF_DISCORD_CHANNEL_ID = 905901970915721257
COMBAT_PATROL_CHANNEL_ID = 1300249480095989760
TNF_ANNOUNCEMENT_CHANNEL_ID = 1119473760525877289
CAT_CHANNEL_ID = 1415227688368607323
TEAM_TOYS_GENERAL_CHANNEL_ID = 1377545202029432855

kittycons = [
    ":3",
    "=3",
    "UwU",
    "OwO",
    ":33",
    "(=^･ω･^=)",
    "(=^‥^=)",
    "(=①ω①=)",
    "(=ＴェＴ=)",
    "(=｀ω´=)",
    "(=^･^=)",
    "(=^-ω-^=)",
    "(=^･ｪ･^=)",
    "(=^･o･^=)",
    "(=^･ｪ･^=)",
    "(=^‥^=)ﾉ",
    "ฅ^•ﻌ•^ฅ",
    "ฅ(＾・ω・＾ฅ)",
    "૮₍｡´ᴖ ˔ ᴖ`｡₎ა",
    "(=①ω①=)ﾉﾞ",
    "(*ΦωΦ*)",
    "(ΦωΦ)",
    "(=ↀωↀ=)",
    "ฅ(•ㅅ•❀)ฅ",
    "(=^･ｪ･^=)っ",
    "(=^･ω･^)y＝",
]

allowed_cat_channels = [CAT_CHANNEL_ID, TEAM_TOYS_GENERAL_CHANNEL_ID]



def is_military_time(time_str):
    military_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    return bool(military_pattern.match(time_str))

def is_standard_time(time_str):
    standard_pattern = re.compile(r'^(1[0-2]|0?[1-9]):[0-5][0-9]\s?(AM|PM|am|pm)$')
    return bool(standard_pattern.match(time_str))

def military_to_standard(military_time):
    if not is_military_time(military_time):
        return "Invalid military time format."
    hours, minutes = map(int, military_time.split(':'))
    period = "AM"
    if hours >= 12:
        period = "PM"
        if hours > 12:
            hours -= 12
    if hours == 0:
        hours = 12
    return f"{hours:02d}:{minutes:02d} {period}"

def time_format_check_and_convert(time_str):
    if is_military_time(time_str):
        return military_to_standard(time_str)
    elif is_standard_time(time_str):
        return time_str
    else:
        return "Invalid time format."

intents = discord.Intents.default()
intents.message_content = True  
intents.guilds = True 

bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)
CORS(app)


MST = zoneinfo.ZoneInfo("America/Denver")  # Mountain Standard/Daylight Time

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    send_cat.start()

@tasks.loop(minutes=1)
async def send_cat():
    now = datetime.datetime.now(MST)
    if now.hour == 10 and now.minute == 0:  # 10:00 AM MST
        channel = bot.get_channel(CAT_CHANNEL_ID)
        if channel:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://cataas.com/cat") as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await channel.send(content="Good meowning! =3",file=discord.File(fp=io.BytesIO(data), filename="cat.jpg"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Prevents the bot from replying to itself

    # Check for a trigger phrase
    if "this is heresy" in message.content.lower():
        file_path = "videos/heresy.mp4"  

        if os.path.exists(file_path):
            video_file = discord.File(file_path, filename="heresy.mp4") 
            await message.reply(file=video_file)
        else:
            await message.reply("Sorry, video not found.")
    elif "kill myself" in message.content.lower() or "kill yourself" in message.content.lower():
        file_path = "videos/neverkys.mp4"
        if os.path.exists(file_path):
            video_file = discord.File(file_path, filename="neverkys.mp4")
            await message.reply(file=video_file)
        else:
            await message.reply("Sorry, video not found.")

    elif "give kitty" in message.content.lower() and message.channel.id in allowed_cat_channels:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cataas.com/cat") as resp:
                if resp.status == 200:
                    data = await resp.read()

                    text = f"{random.choice(kittycons)}"
                    await message.reply(content=text,file=discord.File(fp=io.BytesIO(data), filename="cat.jpg"))
                else:
                    await message.reply("Sorry couldn't fetch 😿")

    # VERY IMPORTANT: This allows other commands/events (like Flask-triggered ones) to still work
    await bot.process_commands(message)

async def post_event(event_data):
    try:
            
        await bot.wait_until_ready()

        general_channel = bot.get_channel(GENERAL_PAIRINGS_CHANNEL_ID)
        if not general_channel:
            print("Error: General channel not found.")
            return False

        # Create embed
        event_title = event_data.get("eventTitle", "Untitled Event")
        event_game = event_data.get("eventGame", "Unknown Game")
        event_description = event_data.get("eventDescription", "Unkown Description")
        event_date_str = event_data.get("eventDate", None)
        event_day = event_data.get("eventDay", "")
        event_time = event_data.get("eventTime", "")
        event_organizer = event_data.get("eventOrganizer", "Unknown Organizer")
        organizer_contact = event_data.get("organizerContactInfo", "No contact info")
        matches = event_data.get("matches", [])
        playerList = event_data.get("playerList", [])
        event_fee = event_data.get("eventFee", "Free")
        event_id = event_data.get("_id")
        isPublished = event_data.get("isPublished")
        event_url = f"https://gamehavenstg.com/events/{event_id}"

        event_fee_display = "FREE" if str(event_fee) in ["0", "0.0", "0.00", "Free", ""] else f"${event_fee}"
        checkIn = "Sign Up" if isPublished == False else ""

        embed = discord.Embed(title=event_title + " " + checkIn, color=discord.Color.blue())

        date_display = "No date provided"
        if event_date_str:
            try:
                date_object = datetime.fromisoformat(event_date_str)
                month_str = date_object.strftime("%B")
                day_num = date_object.day
                date_display = f"**Date:** {month_str} {day_num}, {event_day} at {time_format_check_and_convert(event_time)}"
            except ValueError:
                date_display = f"**Date:** {event_date_str} ({event_day} at {event_time})"
        else:
            date_display = f"**Date:** No date provided ({event_day} at {event_time})"

        embed.add_field(name="Event Details", value=f"**Game:** {event_game}\n{date_display}\n**Fee:** {event_fee_display}\n**Event URL:** {event_url}", inline=False)
        embed.add_field(name="Organizer", value=f"{event_organizer} ({organizer_contact})", inline=False)
        embed.add_field(name="Description", value=f"{event_description}", inline=False)

        pairing_text = ""
        if isPublished == True:
            print("we are published correctly")
            if matches:
                for match in matches:
                    player1 = match.get("player1")
                    player2 = match.get("player2")
                    # is_bye = match.get("isBye", False)
                    
                    # Safe name access
                    player1_name = player1.get('playerName', 'Unknown') if player1 else 'Unknown'
                    player2_name = player2.get('playerName', 'Unknown') if player2 else 'Unknown'

                    if player1 and not player2:
                        pairing_text += f"{player1_name} has a bye.\n"
                    elif player1 and player2:
                        pairing_text += f"{player1_name} vs {player2_name}\n"
                if len(pairing_text) > 1024:
                    pairing_text = pairing_text[:1021] + "..."
                embed.add_field(name="Pairings", value=pairing_text, inline=False)
            else:
                if playerList:
                    player_list_text = "\n".join(f"- {p.get('playerName', 'Unknown')}" for p in playerList)
                    # Truncate player list too
                    if len(player_list_text) > 1024:
                        player_list_text = player_list_text[:1021] + "..."
                    embed.add_field(name="Registered Players", value=player_list_text, inline=False)
                else:
                    embed.add_field(name="Registered Players", value="No players registered.", inline=False)
        # Send embed to general channel
        try:
            await general_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending to general channel: {e}")

        if event_title == "Thursday Night Firefight":
            tnf_channel = bot.get_channel(TNF_PARINGS_CHANNEL_ID)
            tnf_discord = bot.get_channel(TNF_DISCORD_CHANNEL_ID)
            tnf_announcement = bot.get_channel(TNF_ANNOUNCEMENT_CHANNEL_ID)
            try:
                if tnf_channel: await tnf_channel.send(embed=embed)
                if tnf_discord: await tnf_discord.send(embed=embed)
                if tnf_announcement: await tnf_announcement.send(embed=embed)
            except Exception as e:
                print(f"Error sending TNF messages: {e}")

        elif event_title == "Thursday Night Combat Patrol":
            combat_patrol_channel = bot.get_channel(COMBAT_PATROL_CHANNEL_ID)
            tnf_discord = bot.get_channel(TNF_DISCORD_CHANNEL_ID)
            tnf_announcement = bot.get_channel(TNF_ANNOUNCEMENT_CHANNEL_ID)


            if combat_patrol_channel:
                await combat_patrol_channel.send(embed=embed)
                await tnf_discord.send(embed=embed)
                await tnf_announcement.send(embed=embed)

            else:
                print("warning: Combat Patrol channel not found")
        elif event_title == "Test":
            test_channel = bot.get_channel(1118396315559280700)
            if test_channel:
                await test_channel.send(embed=embed)

        return True
    except Exception as e:
        print(f"Critical error in post_event: {e}")
        return False



@app.route('/publish_event', methods=['POST'])
def receive_event():
    if request.is_json:
        print("Event Received")
        event_data = request.get_json()
        print(event_data)
        if event_data:
            asyncio.run_coroutine_threadsafe(post_event(event_data), bot.loop)
            return jsonify({"status": "success", "message": "Event details posted to Discord"}), 200
        else:
            return jsonify({"error": "Missing event data in the JSON payload"}), 400
    else:
        return jsonify({"error": "Request must be JSON"}), 400

def run_flask_app():
    app.run(host='0.0.0.0', port=9999)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    bot.run(BOT_TOKEN)