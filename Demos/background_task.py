import discord
import asyncio

TOKEN = open("/home/pi/Discord/token.txt","r").readline()

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await self.wait_until_ready()
        counter = 0
        channel = self.get_channel(786035683667214396) # channel ID goes here
        while not self.is_closed():
            counter += 1
            await channel.send(counter)
            await asyncio.sleep(60) # task runs every 60 seconds


client = MyClient()
client.run('TOKEN')
