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

bot = commands.Bot(command_prefix=";", intents=intents)  # Prefix is set for non-whitelisted users
# List of whitelisted user IDs
whitelisted_users = []
BOT_OWNER_ID = 1170225052940251196  # Replace with your Discord User ID

#np
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user.name}")
# Dynamic Prefix Handling
@bot.event
async def on_message(message):
    if message.author.bot:  # Ignore bot messages
        return
    # Check if the user is whitelisted
    if message.author.id in whitelisted_users:
        # Try to parse the message as a command without requiring a prefix
        ctx = await bot.get_context(message)
        if ctx.valid:
            await bot.invoke(ctx)
            return
    # Process commands for regular users (with the prefix)
    await bot.process_commands(message)
# Command to add a user to the whitelist
@bot.command(name="np")
async def np(ctx, user: discord.User):
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("You do not have permission to use this command.")
        return
    if user.id not in whitelisted_users:
        whitelisted_users.append(user.id)
        await ctx.send(f"{user.mention} has been added to the no-prefix whitelist.")
    else:
        await ctx.send(f"{user.mention} is already in the no-prefix whitelist.")

# Command to remove a user from the whitelist
@bot.command(name="npr")
async def npr(ctx, user: discord.User):
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("You do not have permission to use this command.")
        return
    if user.id in whitelisted_users:
        whitelisted_users.remove(user.id)
        await ctx.send(f"{user.mention} has been removed from the no-prefix whitelist.")
    else:
        await ctx.send(f"{user.mention} is not in the no-prefix whitelist.")
#np

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
# Flask app for keep-alive

#help command with professional look and interface ..........
from discord.ext import commands
import discord

bot = commands.Bot(command_prefix=";", intents=discord.Intents.default())

@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(
        title="Help - Command List",
        description="Here are all the available commands. Select a category to see more details.",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Moderation",
        value="`ban`, `unban`, `kick`, `mute`, `unmute`, `purge`, `softban`, `warn`",
        inline=False
    )
    embed.add_field(
        name="Utilities",
        value="`role`, `slowmode`, `lock`, `unlock`, `userhistory`, `scam-alert`",
        inline=False
    )
    embed.add_field(
        name="Server Management",
        value="`nuke`, `whitelist`, `prefix`, `status`",
        inline=False
    )
    embed.add_field(
        name="Information",
        value="`help`, `ping`, `botinfo`",
        inline=False
    )

    embed.set_footer(text="Bot by YourName | Use ;help <command> for more info on a command.")

    # Send the help embed
    message = await ctx.send(embed=embed)

    # Add reactions for categories to simulate dropdown-style navigation
    await message.add_reaction("🔧")  # Moderation
    await message.add_reaction("\u2699\ufe0f")  # Utilities (⚙️ in Unicode)
    await message.add_reaction("🛠️")  # Server Management
    await message.add_reaction("ℹ️")  # Information

    # Define the check for reactions
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["🔧", "\u2699\ufe0f", "🛠️", "ℹ️"]

    # Run a loop to handle multiple reactions
    while True:
        reaction, user = await bot.wait_for("reaction_add", check=check)

        # Update the embed based on the category selected
        if str(reaction.emoji) == "🔧":
            # Moderation Commands
            mod_embed = discord.Embed(
                title="Moderation Commands",
                description="Here are all the moderation commands available:",
                color=discord.Color.red()
            )
            mod_embed.add_field(name="`ban`", value="Ban a member from the server.", inline=False)
            mod_embed.add_field(name="`unban`", value="Unban a member using their ID.", inline=False)
            mod_embed.add_field(name="`kick`", value="Kick a member from the server.", inline=False)
            mod_embed.add_field(name="`mute`", value="Mute a member temporarily.", inline=False)
            mod_embed.add_field(name="`unmute`", value="Unmute a member.", inline=False)
            mod_embed.add_field(name="`purge`", value="Purge a certain number of messages.", inline=False)
            mod_embed.add_field(name="`softban`", value="Temporarily ban a member for a specific time.", inline=False)
            mod_embed.add_field(name="`warn`", value="Warn a member for inappropriate behavior.", inline=False)
            await message.edit(embed=mod_embed)

        elif str(reaction.emoji) == "\u2699\ufe0f":
            # Utilities Commands
            util_embed = discord.Embed(
                title="Utilities Commands",
                description="Here are all the utility commands available:",
                color=discord.Color.green()
            )
            util_embed.add_field(name="`role`", value="Assign or remove roles from a member.", inline=False)
            util_embed.add_field(name="`slowmode`", value="Set slowmode for a channel.", inline=False)
            util_embed.add_field(name="`lock`", value="Lock a channel so only admins can send messages.", inline=False)
            util_embed.add_field(name="`unlock`", value="Unlock a channel to allow members to send messages.", inline=False)
            util_embed.add_field(name="`userhistory`", value="View the warning history of a member.", inline=False)
            util_embed.add_field(name="`scam-alert`", value="Alert everyone about a scam in the server.", inline=False)
            await message.edit(embed=util_embed)

        elif str(reaction.emoji) == "🛠️":
            # Server Management Commands
            server_embed = discord.Embed(
                title="Server Management Commands",
                description="Here are all the server management commands available:",
                color=discord.Color.purple()
            )
            server_embed.add_field(name="`nuke`", value="Delete all channels, roles, and everything in the server.", inline=False)
            server_embed.add_field(name="`whitelist`", value="Add or remove users from the whitelist.", inline=False)
            server_embed.add_field(name="`prefix`", value="Set or change the bot prefix.", inline=False)
            server_embed.add_field(name="`status`", value="Change the bot's status.", inline=False)
            await message.edit(embed=server_embed)

        elif str(reaction.emoji) == "ℹ️":
            # Information Commands
            info_embed = discord.Embed(
                title="Information Commands",
                description="Here are the information commands available:",
                color=discord.Color.blue()
            )
            info_embed.add_field(name="`help`", value="Show this help menu.", inline=False)
            info_embed.add_field(name="`ping`", value="Check the bot's latency.", inline=False)
            info_embed.add_field(name="`botinfo`", value="Get information about the bot.", inline=False)
            await message.edit(embed=info_embed)

        # Remove the user's reaction to prevent re-triggering
        await message.remove_reaction(reaction, user)
#help

#bot status 
# Command to change the bot's status dynamically
@bot.command(name="set_status")
async def set_status(ctx, status_type: str, *, status_message: str):
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("You do not have permission to use this command.")
        return
    status_type = status_type.lower()
    activity = None
    if status_type == "playing":
        activity = discord.Game(name=status_message)
    elif status_type == "streaming":
        # Replace with your desired stream URL if necessary
        activity = discord.Streaming(name=status_message, url="https://www.twitch.tv/your_channel")
    elif status_type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=status_message)
    elif status_type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=status_message)
    else:
        await ctx.send("Invalid status type! Use one of: `playing`, `streaming`, `listening`, `watching`.")
        return
    await bot.change_presence(activity=activity)
    await ctx.send(f"Bot status updated to {status_type.capitalize()} **{status_message}**.")
# Bot Status

# Global Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=discord.Embed(
            title="Error: Command Not Found",
            description=f"The command you entered does not exist. Use `;help` to see available commands.",
            color=discord.Color.red()
        ))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=discord.Embed(
            title="Error: Missing Permissions",
            description="You do not have the required permissions to execute this command.",
            color=discord.Color.red()
        ))
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(embed=discord.Embed(
            title="Error: Bot Missing Permissions",
            description="I do not have the required permissions to perform this action.",
            color=discord.Color.red()
        ))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(
            title="Error: Missing Argument",
            description=f"You missed a required argument: `{error.param.name}`. Use `;help <command>` for details.",
            color=discord.Color.red()
        ))
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=discord.Embed(
            title="Error: Invalid Argument",
            description="You provided an invalid argument. Please check and try again.",
            color=discord.Color.red()
        ))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(
            title="Error: Command on Cooldown",
            description=f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            color=discord.Color.orange()
        ))
    elif isinstance(error, commands.NotOwner):
        await ctx.send(embed=discord.Embed(
            title="Error: Owner Only",
            description="This command is restricted to the bot owner.",
            color=discord.Color.red()
        ))
    else:
        await ctx.send(embed=discord.Embed(
            title="Unexpected Error",
            description="An unexpected error occurred. Please contact the bot administrator.",
            color=discord.Color.red()
        ))
        print(f"Ignoring exception in command {ctx.command}: {error}")
# Error Handling

#ban
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, target: discord.Member = None, *, reason="No reason provided"):
    # Check if target is provided or attempt to fetch them by ID
    if not target:
        await ctx.send(embed=discord.Embed(
            title="Error: Missing Member",
            description="Please specify a member to ban. You can mention them or provide their User ID.",
            color=discord.Color.red()
        ))
        return

    try:
        # Attempt to DM the user about the ban
        try:
            dm_embed = discord.Embed(
                title="You have been banned!",
                description=f"You have been banned from **{ctx.guild.name}**.\n**Reason:** {reason}\nIf you believe this was a mistake, please contact the server staff.",
                color=discord.Color.red()
            )
            await target.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="Notice",
                description=f"Could not send a DM to {target.name}. They may have DMs disabled.",
                color=discord.Color.orange()
            ))
        # Ban the member
        await target.ban(reason=f"Banned by {ctx.author.name}: {reason}")
        # Send confirmation embed in the server
        embed = discord.Embed(
            title="Member Banned",
            description=f"**{target}** has been banned from the server.",
            color=discord.Color.red()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        await ctx.send(embed=embed)

    except discord.NotFound:
        await ctx.send(embed=discord.Embed(
            title="Error: Member Not Found",
            description=f"Could not find a member with the ID `{target}`. Please ensure the ID is correct.",
            color=discord.Color.red()
        ))
    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(
            title="Error: Insufficient Permissions",
            description=f"I do not have permission to ban {target.mention}. Please check my role and permissions.",
            color=discord.Color.red()
        ))
    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="Error: Unexpected Issue",
            description=f"An unexpected error occurred: {str(e)}",
            color=discord.Color.red()
        ))
# Allow banning by User ID if the member is not in the server
@bot.command(name="banid")
@commands.has_permissions(ban_members=True)
async def banid(ctx, user_id: int, *, reason="No reason provided"):
    try:
        user = await bot.fetch_user(user_id)  # Fetch user by ID
        # Attempt to DM the user about the ban
        try:
            dm_embed = discord.Embed(
                title="You have been banned!",
                description=f"You have been banned from **{ctx.guild.name}**.\n**Reason:** {reason}\nIf you believe this was a mistake, please contact the server staff.",
                color=discord.Color.red()
            )
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="Notice",
                description=f"Could not send a DM to {user.name}. They may have DMs disabled.",
                color=discord.Color.orange()
            ))
        # Ban the user by ID
        await ctx.guild.ban(discord.Object(id=user_id), reason=f"Banned by {ctx.author.name}: {reason}")
        # Send confirmation embed in the server
        embed = discord.Embed(
            title="User Banned by ID",
            description=f"**{user}** has been banned from the server.",
            color=discord.Color.red()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await ctx.send(embed=embed)

    except discord.NotFound:
        await ctx.send(embed=discord.Embed(
            title="Error: User Not Found",
            description=f"Could not find a user with the ID `{user_id}`. Please ensure the ID is correct.",
            color=discord.Color.red()
        ))
    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(
            title="Error: Insufficient Permissions",
            description=f"I do not have permission to ban this user. Please check my role and permissions.",
            color=discord.Color.red()
        ))
    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="Error: Unexpected Issue",
            description=f"An unexpected error occurred: {str(e)}",
            color=discord.Color.red()
        ))
# ban

#unban
@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason="No reason provided"):
    try:
        # Fetch the user by ID
        user = await bot.fetch_user(user_id)
        # Attempt to unban the user
        await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author.name}: {reason}")
        # DM the user about the unban
        try:
            dm_embed = discord.Embed(
                title="You have been unbanned!",
                description=f"You have been unbanned from **{ctx.guild.name}**.\n**Reason:** {reason}\nYou're welcome to join the server again.",
                color=discord.Color.green()
            )
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="Notice",
                description=f"Could not send a DM to {user.name}. They may have DMs disabled.",
                color=discord.Color.orange()
            ))
        # Send confirmation embed in the server
        embed = discord.Embed(
            title="User Unbanned",
            description=f"**{user}** has been unbanned from the server.",
            color=discord.Color.green()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send(embed=discord.Embed(
            title="Error: User Not Found",
            description=f"Could not find a user with the ID `{user_id}` in the ban list. Please ensure the ID is correct.",
            color=discord.Color.red()
        ))
    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(
            title="Error: Insufficient Permissions",
            description=f"I do not have permission to unban this user. Please check my role and permissions.",
            color=discord.Color.red()
        ))
    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="Error: Unexpected Issue",
            description=f"An unexpected error occurred: {str(e)}",
            color=discord.Color.red()
        ))
#unban

#softban
@bot.command(name="softban")
@commands.has_permissions(ban_members=True)
async def softban(ctx, user: discord.Member | int, duration: str, *, reason="No reason provided"):
    try:
        # Parse the duration
        time_units = {"m": 60, "h": 3600, "d": 86400, "w": 604800}
        time_multiplier = time_units.get(duration[-1].lower())
        if not time_multiplier:
            await ctx.send(embed=discord.Embed(
                title="Invalid Duration",
                description="Duration must end with `m` (minutes), `h` (hours), `d` (days), or `w` (weeks). Example: `10m`, `2h`, `1d`.",
                color=discord.Color.red()
            ))
            return
        time_in_seconds = int(duration[:-1]) * time_multiplier
        # Handle both Member and ID cases
        if isinstance(user, int):  # User is provided as an ID
            user = await bot.fetch_user(user)
            is_member = False
        else:
            is_member = True
        # Ban the user
        await ctx.guild.ban(user, reason=f"Softbanned by {ctx.author.name}: {reason}")
        # DM the user about the softban
        try:
            dm_embed = discord.Embed(
                title="You have been softbanned!",
                description=f"You have been temporarily banned from **{ctx.guild.name}** for **{duration}**.\n**Reason:** {reason}",
                color=discord.Color.red()
            )
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="Notice",
                description=f"Could not send a DM to {user}. They may have DMs disabled.",
                color=discord.Color.orange()
            ))
        # Send confirmation embed in the server
        embed = discord.Embed(
            title="User Softbanned",
            description=f"**{user}** has been temporarily banned from the server for **{duration}**.",
            color=discord.Color.red()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        if is_member and user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)
        # Wait for the duration and unban the user
        await asyncio.sleep(time_in_seconds)
        await ctx.guild.unban(user, reason="Softban duration expired")
        # Notify the server about the unban
        unban_embed = discord.Embed(
            title="User Unbanned",
            description=f"**{user}** has been unbanned after the softban duration.",
            color=discord.Color.green()
        )
        await ctx.send(embed=unban_embed)
    except discord.NotFound:
        await ctx.send(embed=discord.Embed(
            title="Error: User Not Found",
            description=f"Could not find a user with the provided ID or Member: `{user}`.",
            color=discord.Color.red()
        ))
    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(
            title="Error: Insufficient Permissions",
            description="I do not have permission to softban this user. Please check my role and permissions.",
            color=discord.Color.red()
        ))
    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="Error: Unexpected Issue",
            description=f"An unexpected error occurred: {str(e)}",
            color=discord.Color.red()
        ))
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

# Run the bot
keep_alive()
bot.run(TOKEN)
