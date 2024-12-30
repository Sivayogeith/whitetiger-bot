import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import Annotated, TypedDict
from typing import Sequence

load_dotenv()
TOKEN = os.getenv("TOKEN")

class DiscordMessagesState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    author: str

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

class WhiteTigerAI:
    def __init__(self):
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

    def generate_reply(self, author, content):
        state = {
            "messages": [HumanMessage(f"{author}: {content}")],
            "author": author,
        }
        result = self.app.invoke(state, self.config)
        return result["messages"][-1].content

white_tiger_bot = WhiteTigerAI()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot: return
    content = message.content
    author = message.author.name

    if bot.user in message.mentions:
        content = content.split(">")[1:] 
        response = white_tiger_bot.generate_reply(author, content)
        await message.reply(response, mention_author=False)
    await bot.process_commands(message) 

bot.run(TOKEN)