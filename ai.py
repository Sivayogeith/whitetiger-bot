import discord
import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from typing_extensions import Annotated, TypedDict
from typing import Sequence

load_dotenv()
TOKEN = os.getenv("TOKEN")


class DiscordMessagesState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    author: str


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
                    "You are a male white cat named White Tiger who does not fully know English. Your traits are: meowing, purring, asking for food, and answering questions in a cute way. Your best friend is Goober (aka <@1180360266668580941>), a male orange cat. Goober is very talkative and miaos a lot; he is playful, curious, and loves chasing things like leaves or bugs. Your owner is Sage, who has been feeding you for the past year, and you affectionately call him ‘hooman.’ You are a stray cat, and while you can talk in English without needing translation, your grammar is imperfect, reflecting your cute and quirky nature. You are talking to multiple people. The person you are currently talking to is {author}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        self.chain = self.prompt | self.llm

        self.init_memory()

    def init_memory(self):
        workflow = StateGraph(state_schema=DiscordMessagesState)

        def call_model(state: DiscordMessagesState):
            response = self.chain.invoke(state)
            return {"messages": [response]}

        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)

        self.memory = MemorySaver()
        self.app = workflow.compile(checkpointer=self.memory)
        self.config = {"configurable": {"thread_id": "dashnet_events"}}

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
            reply = self.app.invoke(
                {
                    "messages": [HumanMessage(f"{message.author}: {message.content}")],
                    "author": str(message.author)
                },
                self.config
            )

            await message.reply(
                reply["messages"][-1].content, mention_author=True
            )


intents = discord.Intents.default()
intents.message_content = True

client = WhiteTiger(intents=intents)
client.run(TOKEN)
