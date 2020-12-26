# My Bot
print('Loading RPi bot...')

import discord
from discord.ext import commands

import time
#import sched
import asyncio

import RPi.GPIO as GPIO

import random

import picamera

import sys
import os
def wipe(): os.system('clear')

from config import *
# \/ In config.py
#TOKEN = open("/home/pi/Discord/token.txt","r").readline()
#lighttimer
#adminrole
# --

pir1 = 4 #7
relay1 = 14 #8
led1 = 18 #12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(pir1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

bot = commands.Bot(command_prefix='.')
camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
#camera.led = False


@bot.event
async def on_ready():
    #await bot.change_presence(activity=discord.Game('Sea of Thieves'))
    #await bot.change_presence(activity=discord.Streaming(name='Sea of Thieves', url='https://www.twitch.tv/your_channel_here'))
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Boys'))
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Some Custom Beats'))
    """
    ActivityType
      unknown - clears
   
    Status
      online
      idle
     dnd #work sometimes?
     do_not_disturb
    """
    await bot.change_presence(status=discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.listening, name = 'My Masters'))
    #wipe()
    
    print('---Logged in as---')
    print(bot.user.name)
    print(bot.user.id)
    print('------Ready!------')

@bot.command()
async def pic(ctx):
    camera.capture('snap.jpg')
    channel = bot.get_channel(786035683667214396)
    await channel.send(file=discord.File('snap.jpg'))

@bot.command()
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in #d#')
        return
    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)
@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.UserInputError):
        await ctx.send("Invalid input.")
        return

@bot.command()
async def joined(ctx, member: discord.Member):
    await ctx.send('{0.name} joined on {0.joined_at}'.format(member))
@joined.error
async def joined_error(ctx, error):
    if isinstance(error, commands.UserInputError):
        await ctx.send("No user with at name here!.")
        return

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms ')

@bot.command()
@commands.has_role(adminrole)
async def hide(ctx, amount=3) :
    await ctx.channel.purge(limit=amount)
    print(f'Purged {amount} lines - {ctx.message.author.name}   {time.asctime(time.localtime(time.time()))}')
@hide.error
async def hide_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You Cant Hide lines")
        print(f'{ctx.message.author.name} Tried to hide At  {time.asctime(time.localtime(time.time()))}')

@bot.group()
async def led(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'The LED Light is {pinstate(led1)}...')

@led.command(name='off')
@commands.has_role(adminrole)
async def _off(ctx):
    if pinstate(led1) == 'Off':
        await ctx.send('led1 is Off.')
    else:
        await ctx.send('led1 turned Off..')
        GPIO.output(led1, GPIO.LOW)
        print(f'led1 off - {ctx.message.author.name}   {time.asctime(time.localtime(time.time()))}')
@_off.error
async def _off_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You Do Not have permission to do that, Yo!")
        print(f'{ctx.message.author.name} tried to turn the led off At  {time.asctime(time.localtime(time.time()))}')

@led.command(name='on')
@commands.has_role(adminrole)
async def _on(ctx):
    if pinstate(led1) == 'On':
        await ctx.send('led1 is On.')
    else:
        await ctx.send('led1 turned On..')
        GPIO.output(led1, GPIO.HIGH)
        print(f'led1 on  - {ctx.message.author.name}   {time.asctime(time.localtime(time.time()))}')
@_on.error
async def _on_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You Do Not have permission to do that, Yo!")
        print(f'{ctx.message.author.name} tried to turn the led on At  {time.asctime(time.localtime(time.time()))}')

def motion_light(channel):
    moved = time.mktime(time.localtime())
    while GPIO.input(channel) == 0:
        time.sleep(.5)
        if pinstate(relay1) == 'On':
            remaining = lighttimer + moved - time.mktime(time.localtime())
            if remaining <= 0:
                print(f"Relay off - Timeout  {time.asctime(time.localtime(time.time()))}")
                #bot.change_presence(status=discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.listening, name = 'My Master'))
                GPIO.output(relay1, GPIO.LOW)
    while GPIO.input(channel) == 1:
        if pinstate(relay1) == 'Off':
            print(f"Relay on  - Motion   {time.asctime(time.localtime(time.time()))}")
            #bot.change_presence(status=discord.Status.idle, activity = discord.Activity(type = discord.ActivityType.watching, name = 'Movment'))
            GPIO.output(relay1, GPIO.HIGH)
GPIO.add_event_detect(pir1,GPIO.RISING,callback=motion_light,bouncetime=300)

def pinstate(pinname):
    if GPIO.input(pinname):
        return 'On'
    else:
        return 'Off'

async def background_task():
    while True:
        await asyncio.sleep(1)
        #input("Press Enter to continue...")
        #await on_exit()

#bot.loop.create_task(background_task())

"""
alarm_time = '02:30' #24hrs
channel_id = '786035683667214396'
async def time_check():
    await bot.wait_until_ready()
    while True:
        channel = bot.get_channel(channel_id)
        messages = ('Test')
        f = '%H:%M'

        now = time.localtime()
        nowhm =time.strftime(f,now)

        now_h, now_m = map(int, nowhm.split(':'))
        h = now_h * 3600 
        s = now_m * 60
        now_s = h + s

        alarm_h, alarm_m = map(int, alarm_time.split(':'))
        h = alarm_h * 3600 
        s = alarm_m * 60
        alarm_s = h + s

        diff = alarm_s - now_s

        # create a scheduler
        s = sched.scheduler(time.perf_counter, time.sleep)
        # arguments being passed to the function being called in s.enter
        args = (channel, messages)
        # enter the command and arguments into the scheduler
        s.enter(diff, 1, bot.loop.create_task, args)
        s.run() # run the scheduler, will block the event loop
bot.loop.create_task(time_check())
"""
"""
@bot.listen("on_error")
async def on_command_error(self, ctx, error):
    # if command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return
    # get the original exception
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
        await ctx.send(_message)
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send('This command has been disabled.')
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
        return

    if isinstance(error, commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
        await ctx.send(_message)
        return

    if isinstance(error, commands.UserInputError):
        await ctx.send("Invalid input.")
        await self.send_command_help(ctx)
        return

    if isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send('This command cannot be used in direct messages.')
        except discord.Forbidden:
            pass
        return

    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command.")
        return
"""
async def quit_exit():
    print()
    print('Exiting RPi Bot.')
    await bot.change_presence(status=discord.Status.offline, activity = discord.Activity(type = discord.ActivityType.unknown, name = 'bye'))
    await bot.logout()
    await bot.close()
    GPIO.cleanup()
    #time.sleep(1)
    sys.exit
    #wipe()

# Start Bot
print('Starting RPi Bot...')
bot.run(TOKEN)

# Bot exited
print()
print('Humanely Killing RPi Bot.')
GPIO.cleanup()
time.sleep(1)
#wipe()