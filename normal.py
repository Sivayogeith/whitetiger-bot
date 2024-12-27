import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.target_channel = None

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        await self.select_channel()

    async def select_channel(self):
        print("Available channels:")
        for channel in self.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                print(f"{channel.name} (ID: {channel.id})")

        channel_name = input("Enter the name of the channel to use: ")
        for channel in self.get_all_channels():
            if channel.name == channel_name and isinstance(channel, discord.TextChannel):
                self.target_channel = channel
                print(f"Channel set to: {channel.name} (ID: {channel.id})")
                break

        if self.target_channel is None:
            print("Channel not found. Please restart the bot and try again.")
            await self.close()

        await self.message_loop()

    async def on_message(self, message):
        if self.target_channel and message.channel.id == self.target_channel.id and message.author.id != self.user.id:
            print(f"Message from {message.author}: {message.content}")
            reply = input("Reply (leave blank to skip): ")
            if reply:
                await message.reply(reply, mention_author=True)

    async def message_loop(self):
        while True:
            user_input = input("Message to send (or 'exit' to quit): ")
            if user_input.lower() == "exit":
                print("Exiting message loop.")
                await self.close()
                break
            if user_input and self.target_channel:
                await self.target_channel.send(user_input)
                
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)