# No longer shall you be my Doctore.
# You will assume the mantle of lanista,
# and be warmly greeted by your name, Oenomaus. 

# bot.py contains all necessary functions for running of the bot, 
# and will call other files when needed for more specific tasks

# Imports

# Numpy for most things
import numpy as np

# Discord API
import discord 
import asyncio

# Sequence Matcher for testing opening line
from difflib import SequenceMatcher
# from dotenv import load_dotenv
from discord.ext import commands


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
print("Loading environment and authenticating with discord")
print("______\n")

# token is hidden within a separate file 
from keys import TOKEN

@bot.command(name="hello")
async def foo(ctx, arg):
    await ctx.send(arg)

# Print output when bot loads up
@bot.event
async def on_ready():
    print('logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')
    
# Set up the current user as who will be greeted
global current_user
current_user = None

# Set up proper answers to greet in advance
goldenanswer = "Sacred ground Doctore, watered with tears of blood."
sandanswer = "Sand?"

# set up a global variable which stores user responses and saves them
global saved_messages
saved_messages = []

# Load the anime killer model as a class (defined separately)
from animekiller import animeKiller
global model

# default threshold is 0.6. any probability below that will not be classified.
model = animeKiller("model", threshold = 0.65)

# load function to whip anime images to hell
from gifmaker import do_gif

## == HELPER FUNCTIONS, Running of the bot comes later
async def ask_new_recruit(member):

    global saved_messages
    global current_user

    # get role of freshly-bought-slave from channel
    role = discord.utils.get(member.guild.roles, name='freshly-bought-slave')

    # get channel ID of the_sands
    channel = discord.utils.get(member.guild.text_channels, name="the_sands")

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
    print("Sent message to " + member.name)

    # set the global current user as whoever has most recently joined
    current_user = member

    # update saved messages with most recent message
    saved_messages.append(f"Oenomaus: {member.name}, what lies beneath your feet?\n")

async def respond_to_new_recruit(message, channel):

    global saved_messages
    global current_user

    # if no-one has joined, ignore
    if current_user is None:
        return

    # only if the person responding in the_sands is the current_user as defined by the global
    # variable from the on_member_join
    if message.author == current_user:

        # read response
        response = message.content
        print("\n\nNew user response:\n")
        print(response)

        # update saved messages with most response
        saved_messages.append(f"{current_user.name}: {response}\n")

        # use SequenceMatcher to get ratio to either best answer or the sand answer
        r_good = SequenceMatcher(a=response, b=goldenanswer).ratio()
        r_sand = SequenceMatcher(a=response, b=sandanswer).ratio()
        print("\nratio for golden =", r_good, "\n")
        print("\nratio for sand =", r_sand, "\n")

        # get the role ID for freshly bought slave (to remove)
        prev_role = discord.utils.get(message.guild.roles, name='freshly-bought-slave')

        # if the ratio passes the threshold, change role (with some response)
        threshold = 0.7
        if r_good > threshold:

            await asyncio.sleep(1)
            await channel.send("You may join the Ludus.")

            saved_messages.append("Oenomaus: You may join the Ludus.\n")

            await asyncio.sleep(1)
            role2 = discord.utils.get(message.guild.roles, name='Recruit')
            await current_user.add_roles(role2)
            await current_user.remove_roles(prev_role)

        elif r_sand > threshold:

            with open('laughing_gladiators.gif', 'rb') as f:
                picture = discord.File(f)
            await channel.send(file=picture)

            await asyncio.sleep(1.5)
            await channel.send("You will do as commanded, absent complaint, or see flesh stripped from bone.\n")
            await channel.send("Fall in line with other feeble minded recruits.\n")

            saved_messages.append("Oenomaus: You will do as commanded, absent complaint, or see flesh stripped from bone.\n")
            saved_messages.append("Oenomaus: Fall in line with other feeble minded recruits.\n")

            await asyncio.sleep(1)
            role2 = discord.utils.get(message.guild.roles, name='Recruit')
            await current_user.add_roles(role2)
            await current_user.remove_roles(prev_role)
        
        else:
            with open('laughing_gladiators.gif', 'rb') as f:
                picture = discord.File(f)
            await channel.send(file=picture)
            await asyncio.sleep(2)
            await channel.send("You are not fit to be a gladiator.\n")
            saved_messages.append("Oenomaus: You are not fit to be a gladiator.\n")
            await current_user.kick(reason = "Your foolishness has cost a life.  But yours may yet be redeemed -- two fingers, a sign of surrender, a plea of mercy to the Editor of the Games.  Beg for your life, little rabbit.")

        # at the end of an interaction, update the text file with the text
        txt = open('saved_messages.txt', 'a')
        txt.write('\n')
        for j in range(len(saved_messages)):
            txt.write(saved_messages[j])
        txt.write('\n')
        txt.close()

        # reset saved messages
        saved_messages = []

async def detect_anime(message):

    global model

    # print("\n\nChecking if message has anime...\n") 

    is_anime = False
    im_path  = ""

    message_lines = np.array(message.content.split("\n"))

    # Champions get special rules
    role_names = [role.name for role in message.author.roles]
    if "Champion of Capua" in role_names:
        print("Champion detected")
        return False


    # which_urls = np.array([a.startswith("http") for a in message_lines])
    # any_anime_url_names = np.array([a.find("anime") for a in message_lines[which_urls]])
    # first basic check if url contains anime (removing as it's TOO EASY)
    # if any(any_anime_url_names > 0):
    #     return False, True

    # Second check is if an image has been found as an attachment
    if not is_anime and len(message.attachments) > 0:
        
        # there is an attachment, check if it is an image
        attachment = message.attachments[0]
        if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".gif"):
            
            print(f"Found image attachment named {attachment.filename} in message, checking...\n")

            im_path = attachment.url
            is_anime = model.predict(im_path)


            

    # Another check if the message content contains gif from gif keyboard    
    which_gifs1 = np.array(["https://tenor.com/view/" in a for a in message_lines])
    if not is_anime and which_gifs1.any():
    
       print("Found tenor (probably gif) embed in message, checking...")

       # Possible to have multiple embeds, remove message if any are flagged
       any_anime = []
       for embed in message.embeds:
            if (embed.to_dict()["video"]["url"].endswith(".mp4")):
               
                # Tenor keyboard behaves strangely, it doesn't give a direct URL link to
                # the gif, so need to convert it

                # Get video (mp4) URL from the embedded attachment
                video_url = embed.to_dict()["video"]["url"]
                
                # Convert this MP4 to the corresponding tenor GIF URL
                gif_id = video_url[len("https://media.tenor.com/"):-len(".mp4")]
                gif_id  = gif_id.split("/")
                gif_id[0] = gif_id[0][:gif_id[0].find("Po")]
                gif_id[0] = gif_id[0] + "AC"
                gif_id = "/".join(gif_id)
                im_path = "https://c.tenor.com/" + gif_id + ".gif"

                print(f"GIF URL: {im_path}")

                # Finally, predict
                any_anime.append(model.predict(im_path))

            is_anime = any(any_anime)
            

    
    # Next, check for directly embedded gifs (like sent in a message, or gboard)
    which_gifs2 = np.array([a.endswith(".gif") for a in message_lines])    
    if not is_anime and any(which_gifs2):
        
        for im_path in message_lines[which_gifs2]:
            if model.predict(im_path):
                is_anime = True
            
        
        
    # Check for twitter/attached/embedded images:
    if not is_anime and len(message.embeds) > 0:

        for att in message.embeds:
            
            if "thumbnail" in dir(att):
                im_path = att.thumbnail.url
                print(f"\nImage thumbnail detected: {im_path}")
                if model.predict(im_path):
                    is_anime = True
                    break
                

    # Output result
    if is_anime:
        print("I smell some filth (anime detected).\n\n")
    else:
        print("No anime detected\n\n")

    return is_anime, im_path

async def whip_anime(channel, im_path):
    
    do_gif(main_gif_path = "whip.gif", image=im_path)

    await channel.send(file=discord.File("current_whip.gif"))

    
async def remove_anime_message(message, channel):
    await message.delete()
    await channel.send(f"""
        {message.author.name}, we will not tolerate this filth within the Brotherhood. There is only one place for a dog without honour, see yourself to the pits.
    """)

# inbuilt "on member join" function will ping everyone, clear chat and greet
@bot.event
async def on_member_join(member):
    await ask_new_recruit(member)

# predefined "on message" event which reacts to a reply ONLY from current_user
@bot.event
async def on_message(message):

    print(f"({message.channel.name}) {message.author.name}: {message.content}")
    print("\n")

    # print("message guild text channels = ")
    # print(message.guild.text_channels)

    # print("next = ")
    
    # get names of all channels
    # names = np.array([a.name for a in message.guild.text_channels])
    
    # def get_channel_id(name):
    #     pos = np.where(names == pos)[0][0]
    #     return names[pos].id


    # get channel IDs
    the_sands = discord.utils.get(message.guild.text_channels, name="the_sands")
    the_ludus = discord.utils.get(message.guild.text_channels, name="the_ludus")
    
    print("Channel ID = ")
    print(message.channel.id)


    if message.channel.id == the_sands.id:
        await respond_to_new_recruit(message, the_sands)
    if message.channel.id == the_ludus.id:
        is_anime, im_path = await detect_anime(message)
        if is_anime: # remove message if anime and send a message reply
            await whip_anime(the_ludus, im_path)
            await remove_anime_message(message, the_ludus)
    if message.content == "!recruits":
        file = discord.File("saved_messages.txt") 
        await message.channel.send("*Attaching saved new recruitment*", file=file)
    else:
        await bot.process_commands(message)

@bot.command(name="threshold")
async def change_threshold(ctx, *args):
    
    global model 

    admin = discord.utils.get(ctx.guild.roles, name='admin')

    threshold = float(args[0])

    if admin in ctx.author.roles:
        if threshold > 1 or threshold < 0:
            await ctx.send("Foolish. *Threshold must be between 0 and 1.*")
        else:
            print(f"model reloaded with threshold = {threshold}")
            model = animeKiller("model", threshold=threshold)
            await ctx.send("Your will, my hands.")
    else:
        await ctx.send("You are a man who stands only for himself, and would betray the gods to gain what he desires.")


# this always comes at the end
bot.run(TOKEN)
