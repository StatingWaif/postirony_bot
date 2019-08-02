import discord
from discord.ext import commands
from random import choice
import os

filelist = os.listdir('pics')

client = commands.Bot(command_prefix = '!')



@client.event
async def on_ready():
	print('bot is ready')
	await client.change_presence(status=discord.Status.idle, activity=discord.Game('!help для списка всех команд'))

@client.event
async def on_member_join(member):
	print(f'{member} зашёл на сервер')


@client.event
async def on_member_remove(member):
	print(f'{member} вышел в окно')


@client.command()
async def hello(ctx):
	await ctx.send('ты што идиот??? Ты совсем жизнью контуженный? Зачем здороваться с роботом?')


@client.command(aliases=['постироничная_картинка'])
async def postpic(ctx):
	with open(f'pics/{choice(filelist)}', 'rb') as picture:
		file = discord.File(picture)
		await ctx.send(file=file)

client.run(str(os.environ.get('BOT_TOKEN')))
