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
TEAM_TOYS_BOT_CHANNEL_ID = 1418346729429798953
TEAM_TOYS_SLOP_CHANNEL_ID = 1417985931708731473

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
thank_yous = [
    "thanks",
    "thx",
    "tysm",
    "thank u",
    "tyty",
    "ty <3",
    "thx kitty",
    "tyvm",
    "thanks much",
    "thank you"
]
cat_reqs = [
    "cat pls",
    "kitty pls",
    "meow pls",
    "cat now",
    "send cat",
    "gimme cat",
    "more cat",
    "need cat",
    "cat pic",
    "show cat",
    "give kitty",
    "more kitty",
    "give cat",
    "cat please",
    "kitty please",
    "kitty please",

]
your_welcomes = [
    "purrhaps my pleasure =3",
    "no pawblem",
    "always happy to lend a paw!",
    "it’s the least this kitty could do!",
    "you’re pawsitively welcome!",
    "you're welcome :3"
]


quotes = [
    "gonna teach you how to mog",
    "gonna teach you how to get the incel women online",
    "i fear we've already fucked up",
    "you ain't nothing but a hound dog",
    "im a pro kitty. one meow from me could knock ur socks off wise guy",
    "i'm gonna put you on a STRING and dunk you in my personal pain jar",
    "I don't feel pain, regret, sadness, empathy, kindness or anything at all",
    "INDIA RESPECT BUTTON ------> :heart:",
    "this is my world, and in my world all the women are in love with me",
    "man FUCK libraries",
    "I think we should do a Friday night group RP, with me as the alpha male dungeon master",
    "So edgy... so gritty.... so real!!!",
    "THOUGHT ABOUT KILLING MYSELF !!!!!!",
    "hit five days no hoes bouta have a #CumSplosion in my #Jorts",
    "SPREADING THE (EVIL) ENERGY AROUND",
    "Threatening violence over the phone is just another day at the office for me",
    "if my bitch ain't nonbinary... then we gon say 'BYE, NELLY' #ally",
    "I was gon say something perverted but then I realized I'm a cultured and emotionally mature individual",
    "It's just mean girls HQ up in here",
    "Hey if I was in charge of the world... I'd make it super safe for all the um... fishnet adjacent people",
    "Yesssssiirrrr.. UNCLE DANES SERVERS AINT GOT NO HOT SPRAYS LIKE WE DO",
    "If you want to feel comfortable being mean to someone who has never done anything to you you just gotta imagine they did something",
    "I'm worth one william dollars",
    "we fucked bluetooth style",
    "They call me Mr.Booty",
    "you wanna get shredded, patrick bateman style?",
    "I'm gonna hack you",
    "hacked into your computer and I'm downloading all gay pictures. Blackmailed, slut",
    "I HATE THE WOKE because they make women HAIRY in videogames and I only want my women hairy irl",
    "I'm a devout feminist",
    "ugh you always wanna bring your friends when we fuckin :rolling_eyes::pinching_hand: periodt",
    "in here I can be my true incel self and no one will know",
    "be nice.",
    "BE NICE",
    "Time to clean up these streets for the ladies out there",
    "DOWN ON DA FLOO' AND GIVE ME 20 WAPS",
    "Think of the working class...",
    "look babe I just gotta hit the pay dirt on this NFT thing we're gonna be filthy rich!!!!",
    "where's my booty pic at",
    "slurpin on it",
    "If I know no one got me I know carter got me can I get an amen",
    "FREE DIZZY",
    "Bitch you ain't neva met a STONE COLD FEMCEL like me",
    "Eliminate pickle.",
    "its lick yo tail tuesday!",
    "its women wednesday!",
    "Its freak friday!",
    "Bitches be like...'He's MY King'. ME: That's your 4th king this year. The fuck... U playing spades???",
    "yeah what are you, sandwich meat?",
    "and now I have an entire Nation of friends on the internet....",
    "i liek olive gardedn",
    "Hahhahahahahhah DUMB animal",
    "Can i get an inteligent man bitch to show me how to make xbox gifs",
    "SPRINGFEILD OHIO BEST MEALS IN THE U.S.!!!",
    "Men are alowdd to be ugly since they are all #ExpendableWarriors",
    "Can i chill with u to i fw the vibe we have cultivated lets do what feels good",
    "Im sick of all the hater lesbos constantly  trying to ram me off the road and kill me",
    "Ok but why are the suckers and losers trying to kill me today",
    "I need 1 keybump of the Ocean",
    "Hip hop🎶 is peotry✍️",
    "How to i buy trmu 0 dolar outfit",
    "Ive got alot of ideas on berrys that mite get me canceled",
    "Been ages since i had 18 beers almost a full week",
    "Its hard to use parking lot without smashing into lots of other cars  but thabkfuly i think its cheap to get it fixed so no harm no fowl",
    "since nobody wants me  i should jsut  go to the burlap buddy race and  hop somewhere far away",
    "its a doggy dog world",
    "call me a piñata the way stuff comes out when she hits me",
    "mo minecrat mo problems",
    "@grok why do my paws smell like Fritos",
    "I’m crossfaded as f and I’m a dog and I’m eating cheesecake like future",
    "PickleBrothBongWater@gmail.com",
    "https://www.youtube.com/watch?v=TipTOoziFC0 absolute cinema paulie walnuts . jpg",
    "IDWNDP - pickle",
    "Pickles a fool",
    "this chex mix has so much of the flavor powder this kibble is so good rn",
    "go to my bitch ass farm left behind by my grandpa for me instantly start gifting this mean blonde girl all of her favorite gifts before saying hi",
    "i thought maybe i was bubs i thought i twas bubs im not bubs STUPID HANK",
    "hello goat",
    "dude why did this guy post this tiktok his dick is just so obvioius through his pants",
    "PICKLE? YEAH MAN, PICKLE GOOD! MAN, AH YEAH MAN I WANT SOME DAMN PICKLE! YEAH! SO GOOD PICKLE SO GOOD"
]

# dictionary for "give" commands
give_items = {
    "carter": [
        {
            "type": "text",
            "content": [
                "🐐",
                "carter on top!",
                "carter on bottom!",
            ]
        },
        {
            "type": "file",
            "content": ["images/carter1.png", "images/carter2.png", "images/carter3.jpg","images/carter4.png","images/carter5.png"]
        }
    ],
    "pickle": [
        {
            "type": "file",
            "content": ["videos/pickle.mp4", "images/pickle2.png", "gifs/pickle1.gif","images/pickle3.jpg","images/points.png","images/sostands.png","images/staresyou.png","images/thoughtlessbeing.jpg","images/yearyear.png","images/asciimaid.jpg","images/elecmaid.jpg","images/glowingbabything.png","images/kittywonder.jpg","images/myebroom.jpg","images/vlc.png","gifs/strumfast.gif","videos/dapicklelighter.mp4","images/biologicalwaste.png","images/compactdivine.jpg","images/deceased_bunny.png","images/mynameispluto.jpg","images/paperbag_ch.png","images/roecomplex.jpg","images/roverdose.png"],
        }
    ],
    "julia": [
        {
            "type": "file",
            "content": ["gifs/julia1.gif", "gifs/julia2.gif", "gifs/julia3.gif", "gifs/julia4.gif","gifs/julia5.gif","gifs/julia6.gif","images/julia1.png","images/julia2.jpg","images/julia3.png","images/julia4.jpg","images/julia5.jpg","images/julia6.jpg","gifs/julia7.gif","gifs/julia8.gif","gifs/julia9.gif","gifs/julia10.gif","gifs/julia11.gif",]
        }
    ],
    "marcie": [
        {
            "type": "file",
            "content": ["gifs/julia1.gif", "gifs/julia2.gif", "gifs/julia3.gif", "gifs/julia4.gif","gifs/julia5.gif","gifs/julia6.gif","images/julia1.png","images/julia2.jpg","images/julia3.png","images/julia4.jpg","images/julia5.jpg","images/julia6.jpg","gifs/julia7.gif","gifs/julia8.gif","gifs/julia9.gif","gifs/julia10.gif","gifs/julia11.gif",]
        }
    ],
    "dizzy": [
        {
            "type": "file",
            "content": ["gifs/dizzy1.gif","gifs/dizzy2.gif","gifs/dizzy3.gif","gifs/dizzy4.gif","images/dizzy1.jpg"]
        }
    ],
    "minecraft": [
        {
            "type": "file",
            "content": ["videos/minecraft1.mov","images/minecraft1.png","images/minecraft2.png","images/minecraft3.png","images/minecraft4.png","images/minecraft5.png","images/minecraft6.png","images/minecraft7.png","images/minecraft8.png","images/minecraft9.png","images/minecraft10.png","images/minecraft11.png","images/minecraft12.png","images/minecraft13.png","images/minecraft14.png","images/minecraft15.png","images/minecraft16.png","images/minecraft17.png","images/minecraft18.png","images/minecraft19.png","images/minecraft20.png","images/minecraft21.png",]
        }
    ],
    "vis": [
        {
            "type": "file",
            "content":["images/vis9.png","images/vis1.png","gifs/vis1.gif","gifs/vis2.gif","gifs/vis3.gif","gifs/vis4.gif","gifs/vis5.gif","gifs/vis6.gif","gifs/vis7.gif","gifs/vis8.gif","gifs/vis9.gif","gifs/vis10.gif","gifs/vis11.gif","gifs/vis12.gif","images/vis3.jpg","images/vis4.jpg","images/vis5.jpg","images/vis6.jpg","images/vis7.jpg","images/vis8.jpg","gifs/vis3.gif"]
        }
    ],
    "sylvie": [
        {
            "type":"file",
            "content":["images/sylvie1.jpg","images/sylvie2.png","images/sylvie3.jpg","images/sylvie4.jpg","images/sylvie5.jpg","images/sylvie6.jpg","gifs/sylvie1.gif","gifs/sylvie2.gif","gifs/sylvie3.gif","gifs/sylvie4.gif","gifs/sylvie5.gif","gifs/sylvie6.gif","gifs/sylvie7.gif","gifs/sylvie8.gif","gifs/sylvie9.gif","gifs/sylvie10.gif",]
        }
    ],
    "oixo": [
        {
            "type":"file",
            "content":["gifs/oixo1.gif","images/oixo1.png"]
        }
    ],

    "mellohi": [
        {
            "type":"file",
            "content":["images/mellohi4.jpg","images/mellohi5.jpg","images/mellohi6.jpg","images/mellohi7.png","images/mellohi8.png"]
        }
    ],
    "two": [
        {
            "type":"file",
            "content":["gifs/two1.gif","gifs/two2.gif","gifs/two3.gif","gifs/two4.gif","gifs/two5.gif","gifs/two6.gif","gifs/two7.gif","gifs/two8.gif","gifs/two9.gif","gifs/two10.gif","gifs/two11.gif","gifs/two12.gif","gifs/two13.gif"]
        }
    ],
    "man-e": [
        {
            "type":"file",
            "content":["gifs/man1.gif","gifs/man2.gif","gifs/man3.gif","gifs/man4.gif","gifs/man5.gif","gifs/man7.gif","gifs/man8.gif","gifs/man9.gif","gifs/man10.gif","gifs/man11.gif","gifs/man12.gif","gifs/man13.gif","gifs/man14.gif","gifs/man15.gif","gifs/man16.gif","gifs/man17.gif","gifs/man18.gif","gifs/man19.gif","gifs/man20.gif"]
        }
    ],
    "steppa": [
        {
            "type":"file",
            "content":["gifs/steppa1.gif","gifs/steppa2.gif","gifs/steppa3.gif","gifs/steppa4.gif","gifs/steppa5.gif","gifs/steppa6.gif"]
        }
    ],
    "cuck": [
        {
            "type":"file",
            "content":["gifs/cuck1.gif","gifs/cuck2.gif","gifs/cuck3.gif","gifs/cuck4.gif","gifs/cuck5.gif","gifs/cuck6.gif"]
        }
    ],
    "mub": [
        {
            "type":"file",
            "content":["gifs/mub1.gif","gifs/mub2.gif","gifs/mub3.gif","gifs/mub4.gif","gifs/mub5.gif","gifs/mub6.gif","gifs/mub7.gif","gifs/mub8.gif","gifs/mub9.gif","gifs/mub10.gif","gifs/mub11.gif","gifs/mub12.gif","gifs/mub13.gif","gifs/mub14.gif","gifs/mub15.gif","gifs/mub16.gif","gifs/mub17.gif","gifs/mub18.gif","gifs/mub19.gif","gifs/mub20.gif","gifs/mub21.gif","gifs/mub22.gif","gifs/mub23.gif","gifs/mub24.gif","gifs/mub25.gif","gifs/mub26.gif","gifs/mub27.gif","gifs/mub28.gif","gifs/mub29.gif","gifs/mub30.gif","gifs/mub31.gif","gifs/mub32.gif","gifs/mub33.gif","gifs/mub34.gif","gifs/mub35.gif","gifs/mub36.gif",]
        }
    ],
    "kleitor": [
        {
            "type":"file",
            "content":["gifs/kleitor1.gif","gifs/kleitor2.gif"]
        }
    ],
    "rat": [
        {
            "type":"file",
            "content":["gifs/rat1.gif","gifs/rat2.gif","gifs/rat3.gif","gifs/rat4.gif","gifs/rat5.gif","gifs/rat6.gif","gifs/rat7.gif","gifs/rat8.gif","gifs/rat9.gif","gifs/rat10.gif"]
        }
    ],
    "chungy": [
        {
            "type":"file",
            "content":["images/chungus1.jpg","images/chungus1.jpg","images/chungus3.jpg","images/chungus4.jpg","images/chungus5.jpg","images/chungus6.jpg","images/chungus7.jpg","images/chungus8.jpg","images/chungus9.jpg","images/chungus10.jpg","images/chungus11.jpg","images/chungus12.jpg","images/chungus13.png","images/chungus14.png","images/chungus15.jpg","images/chungus16.jpg","images/chungus17.jpg","images/chungus18.jpg","images/chungus19.jpg","images/chungus20.png","images/chungus21.jpg","images/chungus22.jpg","images/chungus23.jpg","images/chungus24.jpg","images/chungus25.jpg","images/chungus26.jpg","images/chungus27.jpg","images/chungus28.jpg","images/chungus29.jpg","images/chungus30.png","gifs/chungus1.gif","gifs/chungus2.gif"]
        }
    ],
    "hank": [
        {
            "type":"file",
            "content":["gifs/hank1.gif","gifs/hank2.gif","gifs/hank3.gif","gifs/hank4.gif","gifs/hank5.gif","gifs/hank6.gif","gifs/hank7.gif","gifs/hank8.gif","gifs/hank9.gif","gifs/hank10.gif","gifs/hank11.gif","gifs/hank12.gif","gifs/hank13.gif","gifs/hank14.gif","gifs/hank15.gif","gifs/hank16.gif","gifs/hank17.gif","gifs/hank18.gif","gifs/hank19.gif","gifs/hank20.gif","images/hank1.jpg", "images/hank2.png"]
        }
    ],
    "aleena": [
        {
            "type":"file",
            "content":["images/aleena1.png","images/aleena2.png","images/aleena3.png","images/aleena4.png","images/aleena5.png","images/aleena6.png","images/aleena7.png","images/aleena8.png","images/aleena9.png","gifs/aleena1.gif","gifs/aleena2.gif"]
        }
    ],
    "avery":[
        {
            "type":"file",
            "content":["images/avery1.jpg","images/avery2.jpg","images/avery3.png","images/avery4.jpg","images/avery5.jpg","images/avery7.png","images/avery8.png","images/avery9.jpg","images/avery10.png","images/avery11.png","images/avery12.jpg","images/avery13.png","images/avery14.jpg","images/avery15.jpg","images/avery16.jpg","images/avery17.png","images/avery18.png","images/avery19.jpg","images/avery20.png","gifs/avery1.gif","gifs/avery2.gif","gifs/avery3.gif"]
            
        }
    ],
    "buggy":[
        {
            "type":"file",
            "content":["gifs/buggy1.gif"]
        }
    ]
}



random_times = []


allowed_cat_channels = [CAT_CHANNEL_ID, TEAM_TOYS_GENERAL_CHANNEL_ID, TEAM_TOYS_SLOP_CHANNEL_ID, TEAM_TOYS_BOT_CHANNEL_ID]



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
    send_quotes.start()
    global random_times
    random_times = schedule_random_times()
    print(f"Scheduled random quote times: {random_times}")


@tasks.loop(minutes=1)
async def send_cat():
    now = datetime.now(MST)
    if now.hour == 10 and now.minute == 0:  # 10:00 AM MST
        channel = bot.get_channel(CAT_CHANNEL_ID)
        if channel:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://cataas.com/cat") as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await channel.send(content="Good meowning! =3",file=discord.File(fp=io.BytesIO(data), filename="cat.jpg"))


def schedule_random_times():
    """Generate two random times today (hour + minute)."""
    times = set()
    while len(times) < 2:
        hour = random.randint(10, 23)   # between 8 AM and 10 PM
        minute = random.randint(0, 59)
        times.add((hour, minute))
    return list(times)

@tasks.loop(minutes=1)
async def send_quotes():
    global random_times
    now = datetime.now(MST)
    current_time = (now.hour, now.minute)

    if current_time in random_times:
        quote = random.choice(quotes)
        channel = bot.get_channel(TEAM_TOYS_GENERAL_CHANNEL_ID)
        if channel:
            await channel.send(f"{quote}")

        random_times.remove(current_time)

        if not random_times:
            random_times = schedule_random_times()
            print(f"Rescheduled new random times: {random_times}")

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
    elif "kill myself" in message.content.lower() or "kill yourself" in message.content.lower() or "killing myself" in message.content.lower():
        file_path = "videos/neverkys.mp4"
        if os.path.exists(file_path):
            video_file = discord.File(file_path, filename="neverkys.mp4")
            await message.reply(file=video_file)
        else:
            await message.reply("Sorry, video not found.")

    elif any(phrase in message.content.lower() for phrase in cat_reqs) and message.channel.id in allowed_cat_channels:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cataas.com/cat") as resp:
                if resp.status == 200:
                    data = await resp.read()
                    text = f"{random.choice(kittycons)}"
                    await message.reply(content=text, file=discord.File(fp=io.BytesIO(data), filename="cat.jpg"))
                else:
                    await message.reply("Sorry couldn't fetch 😿")

    elif any(phrase in message.content.lower() for phrase in thank_yous) and message.channel.id == CAT_CHANNEL_ID:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cataas.com/cat") as resp:
                if resp.status == 200:
                    data = await resp.read()
                    text = f"{random.choice(your_welcomes)}"  # use your_welcomes list here
                    await message.reply(content=text)
                else:
                    await message.reply("Sorry couldn't fetch 😿")




    elif "send quote" in message.content.lower() and message.channel.id == TEAM_TOYS_BOT_CHANNEL_ID:
        quote = random.choice(quotes)
        general_channel = bot.get_channel(TEAM_TOYS_GENERAL_CHANNEL_ID)
        if general_channel:
            await general_channel.send(f"{quote}")
        else:
            await message.reply("guh something went wrong")

    elif message.content.lower().startswith("transmit ") and message.channel.id == TEAM_TOYS_BOT_CHANNEL_ID:
        # Get the text after "transmit "
        transmit_text = message.content[len("transmit "):].strip()

        if not transmit_text:
            await message.reply("no message to transmit")
            return

        general_channel = bot.get_channel(TEAM_TOYS_GENERAL_CHANNEL_ID)
        if general_channel:
            await general_channel.send(transmit_text)
        else:
            await message.reply("guh something went wrong")



    elif message.content.lower().startswith("give ") and message.channel.id in allowed_cat_channels:
        item_name = message.content.lower().split("give ", 1)[1].strip()

        if item_name == "list":
            names_list = []
            for name, items in give_items.items():
                total_content = sum(len(entry["content"]) for entry in items)
                names_list.append(f"- *{name}* ({total_content})")

            response = "__**oomf list**__\n" + "\n".join(names_list)
            await message.reply(response)

        if item_name == "oomf":
            valid_keys = [key for key in give_items.keys() if key != "marcie"]
            random_oomf = random.choice(valid_keys)
            item = random.choice(give_items[random_oomf])
            choice = random.choice(item["content"])
            if item["type"] == "text":
                await message.reply(choice)

            elif item["type"] == "file":
                if os.path.exists(choice):
                    file = discord.File(choice)
                    await message.reply(file=file)
                else:
                    await message.reply("guh something went wrong")

            elif item["type"] == "gif":
                if choice.startswith("http"):
                    await message.reply(choice)
                elif os.path.exists(choice):
                    file = discord.File(choice)
                    await message.reply(file=file)
                else:
                    await message.reply("guh something went wrong")

            elif item["type"] == "url":
                await message.reply(choice)


        elif item_name in give_items:
            item = random.choice(give_items[item_name])
            choice = random.choice(item["content"])

            if item["type"] == "text":
                await message.reply(choice)

            elif item["type"] == "file":
                if os.path.exists(choice):
                    file = discord.File(choice)
                    await message.reply(file=file)
                else:
                    await message.reply("guh something went wrong")

            elif item["type"] == "gif":
                if choice.startswith("http"):
                    await message.reply(choice)
                elif os.path.exists(choice):
                    file = discord.File(choice)
                    await message.reply(file=file)
                else:
                    await message.reply("guh something went wrong")

            elif item["type"] == "url":
                await message.reply(choice)


    elif "carter" in message.content.lower() and message.channel.id in allowed_cat_channels:
        c_random = random.randint(1,7)
        if c_random == 7: 
            await message.add_reaction("🇨")
            await message.add_reaction("🇦")
            await message.add_reaction("🇷")
            await message.add_reaction("🇹")
            await message.add_reaction("🇪")
            await message.add_reaction("®")

    elif message.reference:
        # Check if the message includes a valid name
        content_lower = message.content.lower()
        guess = None
        for name in give_items.keys():
            if name in content_lower:
                guess = name
                break
        if not guess:
            return  # no name mentioned

        try:
            # Fetch the replied-to message
            replied = await message.channel.fetch_message(message.reference.message_id)
        except Exception:
            return  # if the message can't be fetched

        if replied.author != bot.user:
            return  # ignore replies to non-bot messages

        # Determine what the bot posted
        posted_content = None
        if replied.content:
            posted_content = replied.content
        elif replied.attachments:
            posted_content = replied.attachments[0].filename

        if not posted_content:
            return  # nothing to match

        # Check if the content belongs to the guessed person
        for entry in give_items[guess]:
            if entry["type"] == "text" and posted_content in entry["content"]:
                await message.add_reaction("✅")
                return
            elif entry["type"] == "file":
                for path in entry["content"]:
                    if os.path.basename(path) == os.path.basename(posted_content):
                        await message.add_reaction("✅")
                        return

        await message.add_reaction("❌")


    elif "296787239982071809" in message.content.lower() and message.channel.id in allowed_cat_channels:
        c_random = random.randint(1,7)
        if c_random == 7: 
            await message.add_reaction("🇨")
            await message.add_reaction("🇦")
            await message.add_reaction("🇷")
            await message.add_reaction("🇹")
            await message.add_reaction("🇪")
            await message.add_reaction("®")

    elif "goat" in message.content.lower() and message.channel.id in allowed_cat_channels:
        await message.add_reaction("🥛")






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