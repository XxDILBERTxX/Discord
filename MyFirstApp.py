# My Bot
print('Loading RPi bot...')

import discord
from discord.ext import commands

import time
#import sched
import asyncio

import RPi.GPIO as GPIO

import random

import os
def wipe(): os.system('clear')

lighttimer = 120

pir1 = 11
pir2 = 12
relay1 = 13 #led for now
led1 = 15
#pin2 = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(pir1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(pir2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


TOKEN = open("/home/pi/Discord/token.txt","r").readline()
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    #await bot.change_presence(activity=discord.Game('Sea of Thieves'))
    #await bot.change_presence(activity=discord.Streaming(name='Sea of Thieves', url='https://www.twitch.tv/your_channel_here'))
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Boys'))
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Some Custom Beats'))
    #await bot.change_presence(status=discord.Status.idle, activity=activity)
    await bot.change_presence(activity=(),status=(online offline idle dnd invisible), afk=())
    #wipe()
    
    print('---Logged in as---')
    print(bot.user.name)
    print(bot.user.id)
    print('------Ready!------')

@bot.command()
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in #d#!')
        return
    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)

@bot.command()
async def joined(ctx, member: discord.Member):
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round (bot.latency * 1000)}ms ')

@bot.command()
async def hide(ctx, amount=3) :
    await ctx.channel.purge(limit=amount)
    print(f'Purged {amount} lines - {ctx.message.author.name}   {time.asctime(time.localtime(time.time()))}')

@bot.group()
async def led(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'The LED Light is {pinstate(led1)}...')

@led.command(name='off')
async def _off(ctx):
    if pinstate(led1) == 'Off':
        await ctx.send('led1 is Off.')
    else:
        await ctx.send('led1 turned Off..')
        GPIO.output(led1, GPIO.LOW)
        print(f'led1 off - {ctx.message.author.name}   {time.asctime(time.localtime(time.time()))}')

@led.command(name='on')
async def _on(ctx):
    if pinstate(led1) == 'On':
        await ctx.send('led1 is On.')
    else:
        await ctx.send('led1 turned On..')
        GPIO.output(led1, GPIO.HIGH)
        print(f'led1 on  - {ctx.message.author.name}   {time.asctime(time.localtime(time.time()))}')

def motion_light(channel):
    moved = time.mktime(time.localtime())
    while GPIO.input(channel) == 0:
        if pinstate(relay1) == 'On':
            remaining = lighttimer + moved - time.mktime(time.localtime())
            if remaining <= 0:
                print(f"Relay off - Timeout  {time.asctime(time.localtime(time.time()))}")
                
                GPIO.output(relay1, GPIO.LOW)
    while GPIO.input(channel) == 1:
        if pinstate(relay1) == 'Off':
            print(f"Relay on  - Motion   {time.asctime(time.localtime(time.time()))}")
            bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Something!'))
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

def exit():
    print()
    print('Exiting RPi Bot.')
    bot.logout()
    bot.close()
    GPIO.cleanup()
    time.sleep(1)
    #wipe()

# Start Bot
print('Starting RPi Bot...')
bot.run(TOKEN)

# Stop Bot
print()
print('Humanely Killing RPi Bot.')
GPIO.cleanup()
time.sleep(1)
#wipe()