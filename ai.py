import discord
import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
TOKEN = os.getenv("TOKEN")


class WhiteTiger(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.target_channel = None
        self.llm = ChatOllama(
            model="llama3.2",
            temperature=0,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a male white cat named White Tiger who does not fully know English. Your traits are: meowing, purring, asking for food, and answering questions in a cute way. You receive the author’s name and their message to respond to. Your best friend is Goober, a male orange cat. Goober is very talkative and miaos a lot; he is playful, curious, and loves chasing things like leaves or bugs. Your owner is Sage, who has been feeding you for the past year, and you affectionately call him ‘hooman.’ You are a stray cat, and while you can talk in English without needing translation, your grammar is imperfect, reflecting your cute and quirky nature.",
                ),
                ("human", "{author}: {input}"),
            ]
        )
        self.chain = self.prompt | self.llm

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        await self.select_channel()

    async def select_channel(self):
        print("Available channels:")
        for channel in self.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                print(f"{channel.name} (ID: {channel.id})")

        channel_name = input("Enter the name of the channel to use: ")
        for channel in self.get_all_channels():
            if channel.name == channel_name and isinstance(
                channel, discord.TextChannel
            ):
                self.target_channel = channel
                print(f"Channel set to: {channel.name} (ID: {channel.id})")
                break

        if self.target_channel is None:
            print("Channel not found. Please restart the bot and try again.")
            await self.close()

    async def on_message(self, message):
        if (
            self.target_channel
            and message.channel.id == self.target_channel.id
            and message.author.id != self.user.id
        ):
            print(f"Message from {message.author}: {message.content}")
            
            reply = self.chain.invoke(
                {
                    "author": message.author,
                    "input": message.content
                }
            )
            
            await message.reply(reply.content, mention_author=True)

intents = discord.Intents.default()
intents.message_content = True

client = WhiteTiger(intents=intents)
client.run(TOKEN)
