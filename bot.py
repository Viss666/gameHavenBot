

import discord
import json
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
from datetime import datetime
from flask_cors import CORS

import asyncio
from dotenv import load_dotenv
import os


load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GENERAL_PAIRINGS_CHANNEL_ID = 1359343581705539726
TNF_PARINGS_CHANNEL_ID = 1358687166410260602

def military_to_standard(time_str):
    from datetime import datetime
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p").lstrip("0")  # Remove leading zero from hour
    except ValueError:
        return "Invalid time format"



intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)

CORS(app)

async def post_event(event_data):
    await bot.wait_until_ready()  # Ensure bot is ready before sending
    if event_data.get("eventTitle") == "Thursday Night Firefight":
        channel = bot.get_channel(TNF_PARINGS_CHANNEL_ID)
    else:
        channel = bot.get_channel(GENERAL_PAIRINGS_CHANNEL_ID)
    print(f"Attempting to post to channel: {channel}")  # Debug

    if channel:
        event_title = event_data.get("eventTitle", "Untitled Event")
        event_game = event_data.get("eventGame", "Unknown Game")
        event_date_str = event_data.get("eventDate", None)
        event_day = event_data.get("eventDay", "")
        event_time = event_data.get("eventTime", "")
        event_organizer = event_data.get("eventOrganizer", "Unknown Organizer")
        organizer_contact = event_data.get("organizerContactInfo", "No contact info")
        matches = event_data.get("matches", [])
        playerList = event_data.get("playerList", [])  # New field for fallback
        event_fee = event_data.get("eventFee", "Free")
        event_id = event_data.get("_id")
        event_url = f"https://gamehavenstg.com/events/{event_id}"

        # Handle fee
        if str(event_fee) in ["0", "0.0", "0.00", "Free"]:
            event_fee_display = "FREE"
        else:
            event_fee_display = f"${event_fee}"

        embed = discord.Embed(
            title=event_title,
            color=discord.Color.blue()
        )

        date_display = "No date provided"
        if event_date_str:
            try:
                date_object = datetime.fromisoformat(event_date_str)
                month_str = date_object.strftime("%B")
                day_num = date_object.day
                date_display = f"**Date:** {month_str} {day_num}, {event_day} at {event_time}"
            except ValueError:
                date_display = f"**Date:** {event_date_str} ({event_day} at {event_time})"
        else:
            date_display = f"**Date:** No date provided ({event_day} at {event_time})"

        embed.add_field(
            name="Event Details",
            value=f"**Game:** {event_game}\n{date_display}\n**Fee:** {event_fee_display}\n**Event URL:** {event_url}",
            inline=False
        )
        embed.add_field(
            name="Organizer",
            value=f"{event_organizer} ({organizer_contact})",
            inline=False
        )

        pairing_text = ""
        if matches:
            for match in matches:
                player1 = match.get("player1")
                player2 = match.get("player2")
                is_bye = match.get("isBye", False)

                player1_display = f"{player1.get('playerName', 'N/A')} ({player1.get('playerDiscordID', 'N/A')})" if player1 else "N/A"
                player2_display = f"{player2.get('playerName', 'N/A')} ({player2.get('playerDiscordID', 'N/A')})" if player2 else "N/A"

                if  player1 and not player2:
                    pairing_text += f"{player1_display} has a bye.\n"
                elif player1 and player2:
                    pairing_text += f"{player1_display} vs {player2_display}\n"
                elif player1 and not player2 and not is_bye:
                    pairing_text += f"Error: Incomplete match data for {player1_display}\n"
                elif not player1 and player2 and not is_bye:
                    pairing_text += f"Error: Incomplete match data for {player2_display}\n"

            embed.add_field(name="Pairings", value=pairing_text, inline=False)
        else:
            # Show registered players if no matches
            if matches == []:
                player_list_text = "\n".join(
                    f"- {p.get('playerName', 'Unknown')} ({p.get('playerDiscordID', 'N/A')})"
                    for p in playerList
                )

                embed.add_field(name="Registered Players", value=player_list_text, inline=False)
            else:
                embed.add_field(name="Registered Players", value="No players registered.", inline=False)

        print(f"Embed title: {embed.title}")
        print("Attempting to send embed...")

        await channel.send(embed=embed)
        return True
    else:
        print(f"Error: Could not find channel with ID {PAIRINGS_CHANNEL_ID}")
        return False

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

