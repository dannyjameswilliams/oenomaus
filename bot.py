# No longer shall you be my Doctore.
# You will assume the mantle of lanista,
# and be warmly greeted by your name, Oenomaus. 

# bot.py contains all necessary functions for running of the bot, 
# and will call other files when needed for more specific tasks

# split into two 'sections' - functions and bot functions (which need bot to be defined first)

# Imports

# Numpy for most things
import numpy as np

# Discord API
import discord 
from discord.ext import commands
import asyncio

# Sequence Matcher for testing opening line
from difflib import SequenceMatcher

from dotenv import load_dotenv

# Load the anime killer model as a class (defined separately)
from animekiller import animeKiller

# get the discord token from the environment variables
import os
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# load function to whip anime images to pieces
from gifmaker import do_gif

# load chat function
from chat import generate_response, initialise_message_history

# log flag for printing output to console
log = True

# which text channels to monitor for anime detection
noanime_channels = ["the_ludus", "streets-of-capua"]

# which text channel to monitor for new joiners
recruit_channel  = "the_sands"

# name of the role which is given to new joiners
new_role = "freshly-bought-slave"

# name of the role which is given to successful joiners (passed the test)
recruit_role = "Recruit"

# name of the role which is exempt from anime roles (default is champion of capua)
exempt_role = "Champion of Capua"

# name of role of admin role
admin_role = "admin"

# threshold for passing the test of "what lies beneath your feet?"
greeting_pass_threshold = 0.7

# threshold for detecting anime
global anime_threshold
anime_threshold = 0.7

# threshold for being given a warning
warning_threshold = 0.6

# Set up proper answers to greet in advance
goldenanswer = "Sacred ground Doctore, watered with tears of blood."
sandanswer = "Sand?"


# MAIN FUNCTIONS
# --------------


async def ask_new_recruit(member):
    """
    Function to greet a new member who has joined the server.
    If the user does not reply with an answer related to spartacus 
    (proper answers are "sand?" or "Sacred ground Doctore, watered with tears of blood.")
    then they will be kicked from the server.
    """

    # retrieve global variables
    global current_user

    # get role of freshly-bought-slave from channel
    role = discord.utils.get(member.guild.roles, name=new_role)

    # get channel ID of the_sands
    channel = discord.utils.get(member.guild.text_channels, name=recruit_channel)

    # ping everyone then clear the chat after 5 seconds
    await channel.send(member.guild.default_role)
    await channel.send(f"A new slave, {member.name}, has entered the ludus.")
    await asyncio.sleep(5)
    await channel.purge(limit=10000)

    # give new member the role of freshly-bought-slave
    await member.add_roles(role)

    # ask what lies beneath their feet after 1 second
    await asyncio.sleep(1)
    await channel.send(f"{member.name}, what lies beneath your feet?")

    if log:
        print("\n\nNew user joined:\n")
        print(f"Name: {member.name}")
        print("Sent message to " + member.name)

    # set the global current user as whoever has most recently joined
    current_user = member

async def respond_to_new_recruit(message, channel):
    """
    Once the new person has been greeted, this function will respond to their message
    and react accordingly.
    """

    # retrieve global variables
    global current_user

    # if no-one has joined, ignore
    if current_user is None:
        return

    # only if the person responding in the_sands is the current_user as defined by the global
    # variable from the on_member_join
    if message.author == current_user:

        # read response
        response = message.content
    

        # use SequenceMatcher to get ratio to either best answer or the sand answer
        r_good = SequenceMatcher(a=response, b=goldenanswer).ratio()
        r_sand = SequenceMatcher(a=response, b=sandanswer).ratio()

        if log:
            print("\n\nNew user response:")
            print(response)
            print("\nratio for golden =", r_good)
            print("ratio for sand =", r_sand, "\n")

        # get the role ID for freshly bought slave (to remove)
        prev_role = discord.utils.get(message.guild.roles, name=new_role)

        # if the ratio passes the threshold, change role (with some response)

        # response is good and they have said the gladiator answer
        if r_good > greeting_pass_threshold:

            # Wait 1 second and then responsd
            await asyncio.sleep(1)
            await channel.send("You may join the Ludus.")

            # Wait 1 second and then change their role / remove previous role
            await asyncio.sleep(1)
            role2 = discord.utils.get(message.guild.roles, name=recruit_role)
            await current_user.add_roles(role2)
            await current_user.remove_roles(prev_role)

            if log:
                print("User passed the test with golden answer, given Recruit role.\n")

        # response is good and they have said the sand answer
        elif r_sand > greeting_pass_threshold:

            # gladiators laugh at answer like in show (send gif)
            with open('resources/laughing_gladiators.gif', 'rb') as f:
                picture = discord.File(f)
            await channel.send(file=picture)

            # Wait a bit and then respond
            await asyncio.sleep(1.5)
            await channel.send("You will do as commanded, absent complaint, or see flesh stripped from bone.\n")
            await channel.send("Fall in line with other feeble minded recruits.\n")

            # Wait 1 second and change role / remove previous role
            await asyncio.sleep(1)
            role2 = discord.utils.get(message.guild.roles, name='Recruit')
            await current_user.add_roles(role2)
            await current_user.remove_roles(prev_role)

            if log:
                print("User passed the test with sand answer, given Recruit role.\n")
        
        # response is bad, so kick
        else:

            # gladiators laugh at answer like in show (send gif)
            with open('resources/laughing_gladiators.gif', 'rb') as f:
                picture = discord.File(f)
            await channel.send(file=picture)

            # wait 2 seconds, respond, wait a bit more then kick
            await asyncio.sleep(2)
            await channel.send("You are not fit to be a gladiator.\n")

            await asyncio.sleep(5)
            await current_user.kick(reason = "Your foolishness has cost a life.  But yours may yet be redeemed -- two fingers, a sign of surrender, a plea of mercy to the Editor of the Games.  Beg for your life, little rabbit.")

            if log:
                print("User failed the test.\n")


async def detect_anime(message):
    """
    Use the pre-trained deep learning model to detect that
    if a message contains an image, classify it is an anime image or not.
    Multiple different ways an image can appear in a discord message:
     - directly attached to the message
     - embedded in the message e.g. a thumbnail
     - a gif from the gif keyboard or otherwise, different formats have different rules
    """

    # get global model variable
    global model

    # pre-defined variables
    is_anime = False
    warning_anime = False
    im_path  = ""
    message_lines = np.array(message.content.split("\n"))

    # The champion of capua is exempt get special rules
    role_names = [role.name for role in message.author.roles]
    if exempt_role in role_names:
        if log:
            print("User is exempt from anime detection, as they are the Champion of Capua.")
        return False


    # First check: message has an image attachment
    if not is_anime and len(message.attachments) > 0:
        
        # there is an attachment, check if it is an image
        attachment = message.attachments[0]
        if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".gif"):

            im_path = attachment.url
            anime_prob = model.predict(im_path)
            is_anime = anime_prob > anime_threshold
            warning_anime = anime_prob > warning_threshold

            if log:
                print(f"Found image attachment named {attachment.filename} in message, checking...\n")


    # Another check if the message content contains gif from gif keyboard    
    which_gifs1 = np.array(["https://tenor.com/view/" in a for a in message_lines])
    if not is_anime and which_gifs1.any():
    
       print("Found tenor (probably gif) embed in message, checking...")

       # Possible to have multiple embeds, remove message if any are flagged
       any_anime = []
       any_warning_anime = []
       for embed in message.embeds:
            if (embed.to_dict()["video"]["url"].endswith(".mp4")):
               
                # Tenor keyboard behaves strangely, it doesn't give a direct URL link to
                # the gif, so need to convert it

                # Get video (mp4) URL from the embedded attachment
                video_url = embed.to_dict()["video"]["url"]
                
                # Convert this MP4 to the corresponding tenor GIF URL (this is some very specific formulation)
                gif_id = video_url[len("https://media.tenor.com/"):-len(".mp4")]
                gif_id  = gif_id.split("/")
                gif_id[0] = gif_id[0][:gif_id[0].find("Po")]
                gif_id[0] = gif_id[0] + "AC"
                gif_id = "/".join(gif_id)
                im_path = "https://c.tenor.com/" + gif_id + ".gif"

                if log:
                    print(f"Found GIF with URL: {im_path}")

                # Finally, predict
                anime_prob = model.predict(im_path)
                any_anime.append(anime_prob > anime_threshold)
                any_warning_anime.append(anime_prob > warning_threshold)
                
            # single flag from any of the embeds is enough to flag the message
            is_anime = any(any_anime)
            warning_anime = any(any_warning_anime)

    
    # Next, check for directly embedded gifs (like sent in a message, or gboard)
    which_gifs2 = np.array([a.endswith(".gif") for a in message_lines])    # multiple gifs possible?
    if not is_anime and any(which_gifs2):
        
        for im_path in message_lines[which_gifs2]:
            anime_prob = model.predict(im_path)
            is_anime = anime_prob > anime_threshold
            warning_anime = anime_prob > warning_threshold

            if is_anime or warning_anime:
                break
            
            
    # Check for twitter/attached/embedded images:
    if not is_anime and len(message.embeds) > 0:

        for att in message.embeds:
            
            if "thumbnail" in dir(att):
                im_path = att.thumbnail.url

                if log:
                    print(f"\nImage thumbnail detected: {im_path}")

                anime_prob = model.predict(im_path)
                is_anime = anime_prob > anime_threshold
                warning_anime = anime_prob > warning_threshold

                if is_anime or warning_anime:
                    break
                
    if log:
        print(f"Anime detected: {is_anime}")
        print(f"Warning anime detected: {warning_anime}")

    # Return whether anime was detected and the image path (for gif whipping)
    return is_anime, warning_anime, im_path

async def whip_anime(channel, im_path):
    """
    Wrapper for the gifmaker function, which will take an image and whip it to pieces.
    """
    
    # do_gif saves a gif called current_whip.gif in the resources folder
    do_gif(image=im_path)

    # send this gif to the channel
    await channel.send(file=discord.File("resources/current_whip.gif"))

    
async def remove_anime_message(message, channel):
    """
    Simple function, if anime is detected, remove the message and send a reply.
    """
    global message_history
    message_history.append({"role": "user", "content": [{"type": "text", "text": message.content}]})
    message_history.append({"role": "assistant", "content": [{"type": "text", "text": f"{message.author.name}, We will not tolerate this filth within the Brotherhood. There is only one place for a dog without honour, see yourself to the pits. [*You removed their message as it contained an image of anime.*]"}]})
    await message.delete()
    await channel.send(f"""
        {message.author.name}, we will not tolerate this filth within the Brotherhood. There is only one place for a dog without honour, see yourself to the pits.
    """)

async def warning_anime_message(message, channel):
    """
    Send a warning message if anime is detected but not enough to remove the message.
    """
    global message_history
    message_history.append({"role": "user", "content": [{"type": "text", "text": message.content}]})
    message_history.append({"role": "assistant", "content": [{"type": "text", "text": f"{message.author.name}, you are testing my patience. [*You warned them as they sent an image of something that might be anime.*]"}]})
    await channel.send(f"""
        {message.author.name}, you are testing my patience.
    """)

async def respond_to_message(message, channel):
    """
    Respond to a message from a user.
    """
    global message_history
    response, message_history = generate_response(message.content, message_history)
    await channel.send(response)



if __name__ == "__main__":

    # Set up the current user as who will be greeted
    global current_user
    current_user = None

    # default threshold is 0.65. any probability below that will not be classified.
    global model
    model = animeKiller("model", threshold = 0.65)

    # set up message history for chat
    global message_history
    message_history = initialise_message_history()

    # -- Set up bot API

    # permissions so that Oenomaus can change peoples roles
    permissions = discord.Permissions(
        manage_roles = True, 
        manage_guild = True, 
        manage_permissions = True
    )

    # new intents thing - give him all the power
    intents = discord.Intents().all()

    # combine them into a bot
    bot = commands.Bot(
        command_prefix="!", 
        case_insensitive=True, 
        intents=intents, 
        permissions=permissions
    )

    # Load discord environment and bot token (so it can connect to discord servers)
    if log:
        print("Loading environment and authenticating with discord")
        print("______\n")

    # Print output when bot loads up
    @bot.event
    async def on_ready():
        print('logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('-----')

    # inbuilt "on member join" function will ping everyone, clear chat and greet
    @bot.event
    async def on_member_join(member):
        await ask_new_recruit(member)

    # predefined "on message" event which reacts to a reply ONLY from current_user
    @bot.event
    async def on_message(message):

        # ignore messages from Oenomaus
        if message.author.name.lower() == "oenomaus":
            return

        if log:
            print(f"({message.channel.name}) {message.author.name}: {message.content}")
            print("\n")
        
        recruit_channel_0   = discord.utils.get(message.guild.text_channels, name=recruit_channel)

        noanime_channel_ids = []
        for channel in noanime_channels:
            if discord.utils.get(message.guild.text_channels, name=channel) is not None:
                noanime_channel_ids.append(discord.utils.get(message.guild.text_channels, name=channel).id)
        
        if log:
            print(f"Message channel ID = {message.channel.id}")
            print(f"Recruit channel ID = {recruit_channel_0.id}")
            print(f"No anime channel IDs = {noanime_channel_ids}")

        if message.channel.id == recruit_channel_0.id:
            if log:
                print(f"Responding to new recruit in {recruit_channel_0.name}")
            await respond_to_new_recruit(message, recruit_channel_0)
            
        if message.channel.id in noanime_channel_ids:

            if log:
                print(f"Checking for anime in {message.channel.name}")
            
            is_anime, warning_anime, im_path = await detect_anime(message)
            
            if is_anime: # remove message if anime and send a message reply

                if log:
                    print(f"Whipping/removing anime in {message.channel.name}")

                await whip_anime(message.channel, im_path)
                await remove_anime_message(message, message.channel)
            elif warning_anime: # send a warning message
                await warning_anime_message(message, message.channel)
        
        if (
            "oenomaus" in message.content.lower() or 
            "doctore" in message.content.lower() or
            "oen" in message.content.lower() or 
            "dotore" in message.content.lower() or
            "dottore" in message.content.lower() or
            "oenamaus" in message.content.lower() or
            "oenemaus" in message.content.lower() or
            "oenomeus" in message.content.lower() or
            "onomaeus" in message.content.lower() or
            "onamaus" in message.content.lower() or
            "onomeus" in message.content.lower() or
            "oenamaus" in message.content.lower() or
            "oenemaus" in message.content.lower() or
            "oenomeus" in message.content.lower() or
            "oenny" in message.content.lower() 
        ):
            await respond_to_message(message, message.channel)

        await bot.process_commands(message)

    @bot.command(name="threshold")
    async def change_threshold(ctx, *args):
        
        global model 

        admin = discord.utils.get(ctx.guild.roles, name=admin_role)

        threshold = float(args[0])

        if admin in ctx.author.roles:
            if threshold > 1 or threshold < 0:
                await ctx.send("Foolish. *Threshold must be between 0 and 1.*")
            else:
                if log:
                    print(f"model reloaded with threshold = {threshold}")
                model = animeKiller("model", threshold=threshold)
                await ctx.send(f"Your will, my hands. *Threshold = {threshold}*")
        else:
            await ctx.send("You are a man who stands only for himself, and would betray the gods to gain what he desires.")

    # this always comes at the end
    bot.run(TOKEN)