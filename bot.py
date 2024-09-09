import os
import dotenv

import discord
from discord.ext import commands, tasks
from datetime import datetime, UTC
from events_db import Events_DB

dotenv.load_dotenv(override=True)
TOKEN = os.getenv('DISCORD_TOKEN')
events_db = Events_DB('events.db')
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    check_upcoming_events.start()
    print(f'{bot.user} has connected to Discord')

@bot.command(name='echo', help="Responds to a message with the same message")
async def echo(ctx, message:str):
    await ctx.send(message)

@bot.command(name='remind', help="Create a reminder for an event. Format: !remind day/month hour:minute 'message'")
async def add_reminder(ctx, date:str, time:str, event_message:str=''):
    current_time= datetime.now(UTC)
    event_year = current_time.year
    event_time = datetime.strptime(f'{date} {time}', '%d/%m %H:%M')
    if (event_time.month < current_time.month) or (event_time.month == current_time.month and event_time.day < current_time.day):
        event_year = current_time.year+1
    event_time = event_time.replace(year=event_year, tzinfo=UTC)
    id = events_db.add_event(ctx.guild.id, event_time, event_message)
    if id != None:
        await ctx.send(f'Reminder made for event on <t:{int(event_time.timestamp())}:f> with the following id: {id}')
    else:
        await ctx.send(f'Failed to add your event to the database.')

@bot.command(name='delete', help='Deletes a reminder with the given ID')
async def remove_reminder(ctx, id:str):
    if(events_db.remove_event(id)):
        await ctx.send(f'The reminder has been removed')
    else:
        await ctx.send(f'Could not find a reminder with the given ID')

@bot.command(name='init', help='adds server to database')
async def init(ctx):
    if(events_db.add_server(ctx.guild.id)):
        await ctx.send(f'The server was added to the database')
    else:
        await ctx.send(f'The server couldn\'t be added')
    
@bot.command(name='settings', help='Modifies settings for the server. Format: !init channel notification time(minutes) "role"')
async def settings(ctx, channel:str, notification_time: int, role: str):
    channel_id = discord.utils.get(ctx.guild.channels, name=channel).id
    role_id = discord.utils.get(ctx.guild.roles, name=role).id
    if (events_db.modify_server(ctx.guild.id, channel_id, notification_time, role_id)):
        await ctx.send(f'The settings were stored in the database')
    else:
        await ctx.send(f'The settings couldn\'t be stored')

@tasks.loop(seconds=30.0)
async def check_upcoming_events():
    for guild in bot.guilds:
        upcoming_event, server = events_db.check_imminent_event(guild.id) or (None, None)
        if upcoming_event != None:
            channel = guild.get_channel(server.channel_id)
            await channel.send(f"There is an upcoming event in <t:{int(upcoming_event.time.timestamp())}:R>: {upcoming_event.message} <@&{server.role_id}>")
            
        

#@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Your command had too few arguments.")
    elif isinstance(error, ValueError):
        await ctx.send(f"There is something wrong with the values in your command")
    else:
        print(error)

if __name__ == '__main__':
    bot.run(TOKEN)