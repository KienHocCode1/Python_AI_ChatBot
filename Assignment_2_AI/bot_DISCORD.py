""" A basic template for a discord bot."""
import discord
import re
from bot_SHELL import *
class MyClient(discord.Client):
    """Class to represent the Client (bot user)"""

    def __init__(self):
        """This is the constructor. Sets the default 'intents' for the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)


    async def on_ready(self):
        """Called when the bot is fully logged in."""
        print('Logged on as', self.user)


    async def on_message(self, message):
        """Called whenever the bot receives a message. The 'message' object
        contains all the pertinent information."""

        # don't respond to ourselves
        if message.author == self.user:
            return

        #get the utterance and generate the response
        utterance = message.content
        intent = understand(utterance)
        response = generate(intent, utterance) #added 2nd argument: utterance

        #send the response
        await message.channel.send(response)

        #won't respond if not bot-channel
        if message.channel.name != "bot-channel":
            return

        #respond when mentioned
        if self.user in message.mentions:
            await message.channel.send('You mentioned me!!')

        # check message content and respond accordingly
        # utterance = re.sub(r'<@.*>', '', message.content, flags=re.IGNORECASE).strip()
        #if utterance == 'goodbye':
        #    await message.channel.send('byebye')

        global msg
        msg= message

## Set up and log in
client = MyClient()
with open("bot_token.txt") as file:
    token = file.read()

client.run(token)