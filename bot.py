#v1.2.2
#Imports
import discord
import os
import sys
import dotenv
import json
import certifi
import re

from pymongo import *
from bson.objectid import ObjectId
from random import randint, choice
from discord.ext import commands
from discord.utils import get

dotenv.load_dotenv()

#MongoDB twash
client = MongoClient(str(os.getenv("MON_STRING")), tlsCAFile=certifi.where())
db = client["CRBOT2Dat"]
warnsc = db["warns"]

warnid = "000000000000000000010f2c"
emojismade = False

#Regexes
mentionre = re.compile(r"<@[0-9]+>")
mentionre2 = re.compile(r"<@![0-9]+>")
iUAT = re.compile(r".*#[0-9]{4}")

#stuff

pf = "."
bot = commands.Bot(command_prefix=pf)
with open("dat.json", "r") as f:
    #Load crap from data file
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]

@bot.event
async def on_ready():
    #logged in?
    print(f"CRBOT2 has logged on in to Discord as {bot.user}")

#events
@bot.event
async def on_message(message):
    #When someone messages
    if message.author == bot.user:
        #Is the bot messaging.
        return
    
    else:
        global curselist
        for item in curselist:
            if item in str(message.content).lower().replace("```brainfuck", "```bf"):
                #you swore, idot.
                print("somebody swore uh oh")
                await message.delete()
                await message.channel.send(f"Don't swear, {message.author.mention}")
                
        if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str(pf)) and ("announcements" not in message.channel.name.lower()):
            #Did you say bot name?
            await message.channel.send("Hello there, I heard my name?")
                
    await bot.process_commands(message)
#lol 69th line

#test command
@bot.command()
async def test(ctx):
    #test for when I need to do dumb stuff
    pass

#Functions
def g_role(ctx, rname):
    role_t = []
    for item in rname:
        role_t.append(get(ctx.guild.roles, name=str(item)) in ctx.message.author.roles)
        
    out = role_t[0]
    for item in role_t[1:]:
        out = out or item
        
    return out

def isCuboid(ctx):
    #Is message author in ctx me (Cuboid)?
    if (ctx.message.author.id == 588132098875850752) or (ctx.message.author.id == 885900826638442546):
        return True
    
    else:
        return False
    
def isMention(text):
    #Is text a mention?
    global mentionre, mentionre2
    if mentionre.match(text) == None:
        out = False
    
    else:
        out = True
        
    if mentionre2.match(text) == None:
        out = out or False
    
    else:
        out = out or True
        
    return out
    
def idFromMention(mention):
    #Get User ID from mention
    if mention.startswith("<@!"):
        return str(mention)[3:-1]
    
    else:
        return str(mention)[2:-1]
    
def isCB2(text):
    #Is text CRBOT2
    text = text.strip()
    if (text == str(bot.user.name)) or (text == str(bot.user)) or (text == "<@" + str(bot.user.id) + ">") or (text == "<@!" + str(bot.user.id) + ">"):
        return True
    
    else:
        return False
    
def isUserAndTag(text):
    #Checks if the string contains a username and tag
    global iUAT
    if iUAT.match(text.strip()) == None:
        return False
    
    else:
        if len(text.split("#")) != 2:
            return False
        
        else:
            return True

#Commands
@bot.command()
async def ping(ctx):
    #ping pong
    await ctx.send("pong")
    
@bot.command()
async def killcr2(ctx):
    #Kill da bot
    if isCuboid(ctx):
        #r u me or r u admin?
        await ctx.send("Ok, Ending...")
        print("Ending...")
        sys.exit()
        
    else:
        await ctx.send("Why are you trying to kill me? :(")
    
@bot.command(aliases=["no-u"])
async def no_u(ctx, person):
    #no u
    await ctx.send(f"No u, {person}")

@bot.command(aliases=["8ball"])
async def magic8ball(ctx):
    #Magic 8-Ball
    global answers
    await ctx.send(choice(answers))
    
@bot.command()
async def quote(ctx):
    #Spews a random quote in chat.
    global quoteslist
    await ctx.send(choice(quoteslist))
    
@bot.command()
async def shoot(ctx, person):
    #SHOOT PERSON BOOM BOOM CHK CHK PEW! POW POW BOOM CRASH POOM BAM!
    await ctx.send(f"{ctx.message.author.mention} ( う-´)づ︻╦̵̵̿╤──   \\\\(˚☐˚”)/ {person}")
    
@bot.command()
async def warn(ctx, person, *args):
    #Warn person.
    if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
        if not isMention(person):
            await ctx.send(f"That person is not a mention.")
            
        else:
            reason = " ".join(args)
                
            if reason == "" or reason.isspace():
                reason = "no good reason at all"
                
            tempd = warnsc.find_one(
                {
                    "_id": ObjectId(warnid)
                }
            )
            try:
                tempd[str(person)] += 1
                
            except KeyError:
                tempd[str(person)] = 1
                
            warnsc.delete_one(
                {
                    "_id": ObjectId(warnid)
                }
            )
            warnsc.insert_one(tempd)
            
            await ctx.send(f"{person} has been warned by {ctx.message.author.mention} for {reason}!")
        
    else:
        await ctx.send(f"You do not have the sufficient permissions to run this command.")
    
@bot.command()
async def rmwarn(ctx, person, *args):
    #Remove warn from person.
    if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
        if not isMention(person):
            await ctx.send(f"That person is not a mention.")
            
        else:
            reason = " ".join(args)
                
            if reason == "" or reason.isspace():
                reason = "no good reason at all"
                    
            tempd = warnsc.find_one(
                {
                    "_id": ObjectId(warnid)
                }
            )
            try:
                tempd[str(person)] -= 1
                if tempd[str(person)] < 0:
                    tempd[str(person)] = 0
                    
                    await ctx.send(f"{person} doesn't have any warns.")
                    return
                
            except KeyError:
                await ctx.send(f"{person} doesn't have any warns.")
                return
                
            warnsc.delete_one(
                {
                    "_id": ObjectId(warnid)
                }
            )
            warnsc.insert_one(tempd)
            
            await ctx.send(f"A warn has been removed from {person} by {ctx.message.author.mention} for {reason}!")
        
    else:
        await ctx.send(f"You do not have the sufficient permissions to run this command.")
        
@bot.command()
async def warns(ctx, person):
    #Shows warns of person
    if not isMention(person):
        await ctx.send(f"That person is not a mention.")
        
    else:
        tempd = warnsc.find_one(
            {
                "_id": ObjectId(warnid)
            }
        )
        out = str(tempd[str(person)])
        if not bool(int(out) - 1):
            await ctx.send(f"{person} has " + out + " warn!")
            
        else:
            await ctx.send(f"{person} has " + out + " warns!")

@bot.command()
async def warnclear(ctx):
    if g_role(ctx, ["Admin"]):
        tempd = {
            "_id": ObjectId(warnid)
        }
        warnsc.delete_one(
            {
                "_id": ObjectId(warnid)
            }
        )
        warnsc.insert_one(tempd)

@bot.command()
async def kick(ctx, person, *args):
    #kicky
    if isCB2(str(person)):
        await ctx.send(":(")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = " ".join(args)
                
                if reason == "" or reason.isspace():
                    reason = "no good reason at all"
                    
                user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
                user = user[0]
                await user.kick(reason=reason)
                await ctx.send(f"{person} was kicked by {ctx.message.author.mention} for {reason}!")
            
            else:
                await ctx.send("You don't have the proper permissions to do that.")
            
        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def ban(ctx, person, *args):
    #get ban'd
    if isCB2(str(person)):
        await ctx.send("""██╗░░██╗
╚═╝░██╔╝
░░░██╔╝░
░░░╚██╗░
██╗░╚██╗
╚═╝░░╚═╝
""")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = " ".join(args)
                
                if reason == "" or reason.isspace():
                    reason = "no good reason at all"
                    
                user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
                try:
                    user = user[0]
                    
                except IndexError:
                    await ctx.send("hey bub that person doesn't exist, or some error has been thrown")
                    await ctx.send("(if that person does exist, notify Cuboid_Raptor#7340)")
                    return
                
                await user.ban(reason=reason)
                await ctx.send(f"{person} was banned by {ctx.message.author.mention} for {reason}!")
            
            else:
                await ctx.send("You don't have the proper permissions to do that.")
            
        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def unban(ctx, person, *args):
    #unban ppl
    if isCB2(str(person)):
        await ctx.send("Thanks for the attempt, but I haven't been banned in this server yet :)")
        
    else:
        if isUserAndTag(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = " ".join(args)
                
                if reason == "" or reason.isspace():
                    reason = "no good reason at all"
                    
                mname, mdisc = person.split("#")
                
                banned_users = await ctx.message.guild.bans()
                for ban_entry in banned_users:
                    user = ban_entry.user
                    
                    if (user.name, user.discriminator) == (mname, mdisc):
                        await ctx.message.guild.unban(user)
                        await ctx.message.channel.send(f"{user.mention} has been unbanned by {ctx.message.author.mention} for {reason}!")
            
            else:
                await ctx.send("You don't have the proper permissions to do that.")
            
        else:
            await ctx.send("That person isn't a Username and Tag seperated by \"#\".")

@bot.command()
async def emojis(ctx):
    if emojismade:
        return
    
    else:
        with open("logo.png", "rb") as f:
            CRBOT2e = await bot.create_custom_emoji(ctx.guild, name="CRBOT2", image=f)

#R U N .   
bot.run(str(os.getenv("DISCORD_TOKEN")))