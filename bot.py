import discord
import json
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
from datetime import datetime
from flask_cors import CORS
import re
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GENERAL_PAIRINGS_CHANNEL_ID = 1359343581705539726
TNF_PARINGS_CHANNEL_ID = 1119468407084023930
TNF_DISCORD_CHANNEL_ID = 905901970915721257
COMBAT_PATROL_CHANNEL_ID = 1300249480095989760

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
bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)
CORS(app)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Prevents the bot from replying to itself

    # Check for a trigger phrase
    if "heresy" in message.content.lower():
        file_path = "videos/heresy.mp4"  

        if os.path.exists(file_path):
            video_file = discord.File(file_path, filename="heresy.mp4") 
            await message.reply(file=video_file)
        else:
            await message.reply("Sorry, video not found.")
    else if "kill yourself" or "kys" in message.content.lower():
        file_path = "videos/neverkys.mp4"
        if os.path.exists(file_path):
            video_file = discord.File(file__path, filename="neverkys.mp4")
            await message.replay(file=video_file)
        else:
            await message.reply("Sorry, video not found.")

    # VERY IMPORTANT: This allows other commands/events (like Flask-triggered ones) to still work
    await bot.process_commands(message)

async def post_event(event_data):
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

    event_fee_display = "FREE" if str(event_fee) in ["0", "0.0", "0.00", "Free"] else f"${event_fee}"
    checkIn = "Check In" if isPublished == False else ""

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
    if isPublished:
        if matches:
            for match in matches:
                player1 = match.get("player1")
                player2 = match.get("player2")
                is_bye = match.get("isBye", False)
                player1_display = f"{player1.get('playerName', 'N/A')} ({player1.get('playerDiscordID', 'N/A')})" if player1 else "N/A"
                player2_display = f"{player2.get('playerName', 'N/A')} ({player2.get('playerDiscordID', 'N/A')})" if player2 else "N/A"

                if player1 and not player2:
                    pairing_text += f"{player1_display} has a bye.\n"
                elif player1 and player2:
                    pairing_text += f"{player1_display} vs {player2_display}\n"
                elif player1 and not player2 and not is_bye:
                    pairing_text += f"Error: Incomplete match data for {player1_display}\n"
                elif not player1 and player2 and not is_bye:
                    pairing_text += f"Error: Incomplete match data for {player2_display}\n"
            embed.add_field(name="Pairings", value=pairing_text, inline=False)
        else:
            if playerList:
                player_list_text = "\n".join(f"- {p.get('playerName', 'Unknown')} ({p.get('playerDiscordID', 'N/A')})" for p in playerList)
                embed.add_field(name="Registered Players", value=player_list_text, inline=False)
            else:
                embed.add_field(name="Registered Players", value="No players registered.", inline=False)

    # Send embed to general channel
    await general_channel.send(embed=embed)

    if event_title == "Thursday Night Firefight":
        tnf_channel = bot.get_channel(TNF_PARINGS_CHANNEL_ID)
        tnf_discord = bot.get_channel(TNF_DISCORD_CHANNEL_ID)
        if tnf_channel:
            await tnf_channel.send(embed=embed)
            await tnf_discord.send(embed=embed)
        else:
            print("Warning: TNF channel not found.")
    elif event_title == "Combat Patrol":
        combat_patrol_channel = bot.get_channel(COMBAT_PATROL_CHANNEL_ID)
        tnf_discord = bot.get_channel(TNF_DISCORD_CHANNEL_ID)

        if combat_patrol_channel:
            await combat_patrol_channel.send(embed=embed)
            await tnf_discord.send(embed=embed)

        else:
            print("warning: Combat Patrol channel not found")

    return True

@app.route('/publish_event', methods=['POST'])
def receive_event():
    if request.is_json:
        event_data = request.get_json()
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