# My Bot
print('Loading RPi bot...')

import discord
from discord.ext import commands

import time
import asyncio

import RPi.GPIO as GPIO

import random

import os
def wipe(): os.system('clear')

lighttimer = 60

pir = 11
relay1 = 13
led1 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(pir, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

TOKEN = open("/home/pi/Discord/token.txt","r").readline()
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    #await bot.change_presence(activity=discord.Game('Sea of Thieves'))
    #await bot.change_presence(activity=discord.Streaming(name='Sea of Thieves', url='https://www.twitch.tv/your_channel_here'))
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Boys'))
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Some Custom Beats'))
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

def pir_motion(channel):
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
            GPIO.output(relay1, GPIO.HIGH)
GPIO.add_event_detect(pir,GPIO.RISING,callback=pir_motion,bouncetime=300)

def pinstate(pinname):
    if GPIO.input(pinname):
        return 'On'
    else:
        return 'Off'

#timertime = 0
#message = "Ding"
#async def timer_task():
#    while timertime > 0:
#        await asyncio.sleep(timertime)
#        await bot.get_channel(786035683667214396).send(message)
#bot.loop.create_task(timer_task())

async def background_task():
    while True:
        await asyncio.sleep(1)
        pass
bot.loop.create_task(background_task())

"""
alarm_time = '20:04'#24hrs
channel_id = '786035683667214396'
async def time_check():
    await bot.wait_until_ready()
    while True:
        channel = bot.get_channel(channel_id)
        messages = ('Test')
        f = '%H:%M'

        #tm_year=2020, tm_mon=12, tm_mday=13, tm_hour=20, tm_min=9, tm_sec=18, tm_wday=6, tm_yday=348, tm_isdst=0
        #tm_year=1900, tm_mon=1, tm_mday=1, tm_hour=20, tm_min=4, tm_sec=0, tm_wday=0, tm_yday=1, tm_isdst=-1

        now = time.localtime()
        print(f'now {now}')
        nowhm =time.strftime(f,now)
        print(f'nowhm {nowhm}')
        nowsec = time.mktime(now)
        print(f'nowsec {nowsec}')
        
        #tt1 =time.strptime(nowhm,f)
        #print(f'tt1 {tt1}')
        #tt2 = time.strptime(alarm_time,f)
        #print(f'tt2 {tt2}')

        #tt1a = time.mktime(tt1)
        #print(f'tt1a {tt1a}')
        #tt2a = time.mktime(tt2)
        #print(f'tt2a {tt2a}')

        # get the difference between the alarm time and now
        #diff = (time.strftime(f,alarm_time) - time.strftime(f,now)).total_seconds()
        #diff = time.mktime(alarm_time) - time.time()
        #diff = (alarm_time - now)
        #diff = (time.strptime(alarm_time,f) - time.strptime(now,f)).total_seconds()  
        print(datetime.timedelta(nowhm - alarm_time))
        diff = (time.timedelta(alarm_time,f) - nowhm)

        # create a scheduler
        print(f'diff {diff}')
        s = sched.scheduler(time.perf_counter, time.sleep)
        # arguments being passed to the function being called in s.enter
        args = (bot.send_message(channel, messages), )
        # enter the command and arguments into the scheduler
        s.enter(5, 1, bot.loop.create_task, args)
        s.run() # run the scheduler, will block the event loop
bot.loop.create_task(time_check())
"""

def on_exit():
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
#time.sleep(1)
#wipe()