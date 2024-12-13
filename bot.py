import discord
from discord.ext import commands
from flask import Flask
import threading
import os
import asyncio
from dotenv import load_dotenv
import logging

# Load the token from the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("discord")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True  # Required for member join/leave events
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix=";", intents=intents)

bot.remove_command("help")

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    threading.Thread(target=run).start()

# Bot Status
@bot.command()
@commands.has_permissions(administrator=True)
async def status(ctx, status_type: str, *, name: str = "Sun MC Network"):
    """
    Change the bot's status dynamically.
    Status Types:
    - active: Displays a standard "Playing" activity.
    - streaming: Displays a "Streaming" activity with a link.
    """
    try:
        if status_type.lower() == "active":
            activity = discord.Game(name=name)
        elif status_type.lower() == "streaming":
            activity = discord.Streaming(name=name, url="https://www.twitch.tv/sunmc0069")  # Replace with a valid URL
        else:
            await ctx.send("Invalid status type! Use `active` or `streaming`.")
            return

        await bot.change_presence(activity=activity)
        embed = discord.Embed(
            title="Bot Status Updated",
            description=f"Bot status set to **{status_type.capitalize()}** with name: **{name}**",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")



# Error Handling
#@bot.event
#async def on_command_error(ctx, error):
#    if isinstance(error, commands.MissingPermissions):
#        await ctx.send("You don't have the required permissions to use this command.")
#    elif isinstance(error, commands.MissingRequiredArgument):
#        await ctx.send("Missing arguments. Please check the command syntax.")
#    elif isinstance(error, commands.CommandNotFound):
#        await ctx.send("Command not found. Use `;help` to see available commands.")
#    else:
#        await ctx.send("An error occurred.")
#        logger.error(f"Error in command {ctx.command}: {error}")
# Error Handling


#Ban
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """
    Ban a member, notify them via DM, and log the punishment.
    """
    try:
        # DM the user about the ban
        dm_embed = discord.Embed(
            title="You Have Been Banned",
            description=f"You have been banned from {ctx.guild.name}.",
            color=0xff0000
        )
        dm_embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
        dm_embed.set_footer(text=f"Moderator: {ctx.author.name}")
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        await ctx.send(f"Could not DM {member.mention} about the ban.")
    # Ban the member
    await member.ban(reason=reason)
    # Log the punishment
    user_id = str(member.id)
    if user_id not in punishments:
        punishments[user_id] = []
    punishments[user_id].append({"type": "Ban", "reason": reason, "moderator": ctx.author.name})
    # Send confirmation in the server
    embed = discord.Embed(
        title="Member Banned",
        description=f"{member.mention} has been banned.",
        color=0xff0000
    )
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
    embed.set_footer(text=f"Action performed by: {ctx.author.name}")
    await ctx.send(embed=embed)
#Ban

#unban
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title="Member Unbanned", description=f"{user.name}#{user.discriminator} has been unbanned.", color=0x00ff00)
            await ctx.send(embed=embed)
            return
    await ctx.send("User not found.")
#unban

#softban
@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(ctx, member: discord.Member, *, reason=None):
    try:
        # Ban the member and delete their message history
        await member.ban(reason=reason, delete_message_days=7)
        # Immediately unban the member
        await ctx.guild.unban(member, reason="Softban: Immediate unban after ban")
        
        # Send confirmation embed
        embed = discord.Embed(
            title="Member Softbanned",
            description=f"{member.mention} was softbanned.\nReason: {reason if reason else 'No reason provided'}",
            color=0xffa500
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I do not have permission to softban this member.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while trying to softban the member: {e}")
#softban

#kick
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """
    Kick a member and send them a DM with the reason.
    Logs the punishment and confirms the action in the channel.
    """
    try:
        # Print to help debug
        print(f"Attempting to kick {member.name} from {ctx.guild.name}")
        # Send DM to the user being kicked
        try:
            dm_embed = discord.Embed(
                title="You Have Been Kicked",
                description=f"You have been kicked from {ctx.guild.name}.",
                color=0xff0000
            )
            dm_embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
            dm_embed.set_footer(text=f"Moderator: {ctx.author.name}")
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"Could not DM {member.name}. They might have DMs disabled.")
            await ctx.send(f"Could not DM {member.mention} about the kick.")
        #Kick the member
        await member.kick(reason=reason)
        print(f"{member.name} has been kicked successfully.")
        #Confirm in the server
        embed = discord.Embed(
            title="Member Kicked",
            description=f"{member.mention} has been kicked.",
            color=0xffa500
        )
        embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
        embed.set_footer(text=f"Action performed by: {ctx.author.name}")
        await ctx.send(embed=embed)

    except discord.Forbidden:
        print("Bot does not have permission to kick this member.")
        await ctx.send("I don't have permission to kick this member.")
    except discord.HTTPException as e:
        print(f"HTTPException occurred: {e}")
        await ctx.send(f"An error occurred while trying to kick the member: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await ctx.send("An unexpected error occurred.")
#kick

#mute
@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason=None):
    """
    Mute a member, optionally for a specified duration, notify them via DM, and log the punishment.
    Duration formats: '10s', '5m', '1h', '1d', '1w'.
    """
    # Retrieve or create the Muted role
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, add_reactions=False)
    # Add the Muted role
    await member.add_roles(muted_role, reason=reason)
    # Calculate mute duration
    duration_seconds = None
    if duration:
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        unit = duration[-1]
        if unit in time_units and duration[:-1].isdigit():
            duration_seconds = int(duration[:-1]) * time_units[unit]
        else:
            await ctx.send("Invalid duration format. Use `s`, `m`, `h`, `d`, or `w` (e.g., `10s`, `1h`).")
            return
    #DM the user about the mute
    try:
        dm_embed = discord.Embed(
            title="You Have Been Muted",
            description=f"You have been muted in {ctx.guild.name}.",
            color=0xffa500
        )
        dm_embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
        if duration_seconds:
            dm_embed.add_field(name="Duration", value=duration, inline=False)
        else:
            dm_embed.add_field(name="Duration", value="Indefinite", inline=False)
        dm_embed.set_footer(text=f"Moderator: {ctx.author.name}")
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        await ctx.send(f"Could not DM {member.mention} about the mute.")
    # Log the punishment
    user_id = str(member.id)
    if user_id not in punishments:
        punishments[user_id] = []
    punishment_entry = {
        "type": "Mute",
        "reason": reason,
        "moderator": ctx.author.name,
        "duration": duration if duration else "Indefinite"
    }
    punishments[user_id].append(punishment_entry)
    # Notify in the server
    embed = discord.Embed(
        title="Member Muted",
        description=f"{member.mention} has been muted.",
        color=0xffa500
    )
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
    if duration_seconds:
        embed.add_field(name="Duration", value=duration, inline=False)
    else:
        embed.add_field(name="Duration", value="Indefinite", inline=False)
    embed.set_footer(text=f"Action performed by: {ctx.author.name}")
    await ctx.send(embed=embed)
    # If duration is specified, automatically unmute after the duration
    if duration_seconds:
        await asyncio.sleep(duration_seconds)
        await member.remove_roles(muted_role)
        try:
            unmute_dm_embed = discord.Embed(
                title="You Have Been Unmuted",
                description=f"Your mute duration in {ctx.guild.name} has ended.",
                color=0x00ff00
            )
            await member.send(embed=unmute_dm_embed)
        except discord.Forbidden:
            pass
        unmute_embed = discord.Embed(
            title="Member Unmuted",
            description=f"{member.mention} has been unmuted.",
            color=0x00ff00
        )
        await ctx.send(embed=unmute_embed)
#mute

#unmute
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if hasattr(bot, "muted_members") and member.id in bot.muted_members:
        previous_roles = bot.muted_members.pop(member.id)
        
        # Remove the muted role and restore previous roles
        if muted_role in member.roles:
            await member.remove_roles(muted_role, reason="Unmuted by command")
        await member.add_roles(*previous_roles, reason="Unmuted by command")
        
        await ctx.send(f"{member.mention} has been unmuted and their roles have been restored.")
    else:
        await ctx.send("No muted roles were recorded for this member, or they were not muted.")
#unmute

#purge
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit)
    embed = discord.Embed(title="Messages Purged", description=f"{limit} messages have been cleared.", color=0x0000ff)
    await ctx.send(embed=embed, delete_after=5)
#purge

#role
@bot.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, *, role: discord.Role):
    """
    Add or remove a role from a member.
    """
    # Check if the bot has higher role hierarchy
    if ctx.guild.me.top_role <= role:
        embed = discord.Embed(
            title="Role Error",
            description="I cannot assign or remove this role because it is higher than or equal to my highest role.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    # Check if the member already has the role
    if role in member.roles:
        # Remove the role
        await member.remove_roles(role)
        embed = discord.Embed(
            title="Role Removed",
            description=f"The role **{role.name}** has been removed from {member.mention}.",
            color=0xff0000
        )
    else:
        # Add the role
        await member.add_roles(role)
        embed = discord.Embed(
            title="Role Added",
            description=f"The role **{role.name}** has been added to {member.mention}.",
            color=0x00ff00
        )

    embed.set_footer(text=f"Action performed by: {ctx.author.name}")
    await ctx.send(embed=embed)
#role

#userhistory
# Global dictionary to track user punishments
if not hasattr(bot, "punishment_history"):
    bot.punishment_history = {}
# Helper Function to Add a Punishment
def add_punishment(member_id: int, punishment_type: str):
    if member_id not in bot.punishment_history:
        bot.punishment_history[member_id] = []
    bot.punishment_history[member_id].append(punishment_type)
# Command to Display User's Punishment History
@bot.command()
@commands.has_permissions(manage_roles=True)
async def userhistory(ctx, member: discord.Member):
    member_id = member.id
    history = bot.punishment_history.get(member_id, [])
    
    if history:
        embed = discord.Embed(
            title=f"Punishment History for {member}",
            description="Here are the recorded punishments:",
            color=0xff0000
        )
        for index, punishment in enumerate(history, 1):
            embed.add_field(name=f"#{index}", value=punishment, inline=False)
        embed.set_footer(text=f"Total punishments: {len(history)}")
    else:
        embed = discord.Embed(
            title=f"No Punishments Found for {member}",
            description="This user has a clean record!",
            color=0x00ff00
        )
    
    await ctx.send(embed=embed)
#userhistory

#warn
@bot.command()
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    # Log the warning
    punishment_type = f"Warning - Reason: {reason if reason else 'No reason provided'}"
    add_punishment(member.id, punishment_type)
    
    # Create an embed for the warning
    embed = discord.Embed(
        title="User Warned",
        description=f"{member.mention} has been warned.",
        color=0xffa500
    )
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
    embed.set_footer(text=f"Issued by: {ctx.author.name}")
    
    await ctx.send(embed=embed)

    # Optionally DM the user about the warning
    try:
        dm_embed = discord.Embed(
            title="You Have Been Warned",
            description=f"You were warned in {ctx.guild.name}.",
            color=0xffa500
        )
        dm_embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
        dm_embed.set_footer(text=f"Issued by: {ctx.author.name}")
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        await ctx.send(f"Could not DM {member.mention} about the warning.")
#warn

#lock 
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, *, reason=None):
    # Get the @everyone role
    everyone_role = ctx.guild.default_role
    channel = ctx.channel

    # Modify permissions to lock the channel
    await channel.set_permissions(everyone_role, send_messages=False)

    # Create an embed for feedback
    embed = discord.Embed(
        title="Channel Locked",
        description=f"{channel.mention} has been locked.",
        color=0xff0000
    )
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
    embed.set_footer(text=f"Locked by: {ctx.author.name}")

    await ctx.send(embed=embed)
#lock 

#unlock
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    # Get the @everyone role
    everyone_role = ctx.guild.default_role
    channel = ctx.channel

    # Modify permissions to unlock the channel
    await channel.set_permissions(everyone_role, send_messages=True)

    # Create an embed for feedback
    embed = discord.Embed(
        title="Channel Unlocked",
        description=f"{channel.mention} has been unlocked.",
        color=0x00ff00
    )
    embed.set_footer(text=f"Unlocked by: {ctx.author.name}")

    await ctx.send(embed=embed)
#unlock

#slowmode
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, delay: int = 0):
    """
    Set a slow mode delay for the channel.
    :param delay: The delay in seconds (0 to disable slow mode).
    """
    if delay < 0:
        await ctx.send("The delay must be a positive number or zero to disable slow mode.")
        return
    
    # Set the slowmode delay
    await ctx.channel.edit(slowmode_delay=delay)

    # Create an embed for feedback
    if delay == 0:
        embed = discord.Embed(
            title="Slow Mode Disabled",
            description=f"{ctx.channel.mention} now has no slow mode.",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="Slow Mode Enabled",
            description=f"{ctx.channel.mention} now has a slow mode delay of {delay} seconds.",
            color=0xffa500
        )
    
    embed.set_footer(text=f"Set by: {ctx.author.name}")
    await ctx.send(embed=embed)
#slowmode

# Help Command
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", description="Here are the available commands:", color=0x00ff00)
    embed.add_field(name="Moderation", value="`ban`, `unban`, `softban`, `kick`, `mute`, `unmute`, `purge`, `role`, `userhistory`, `warn`, `lock`, `unlock`, `slowmode`", inline=False)
    embed.set_footer(text="Developed with ❤️ By The avoxz")
    await ctx.send(embed=embed)

# Run the bot
keep_alive()
bot.run(TOKEN)
