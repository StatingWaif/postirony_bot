import discord
from discord.ext import commands
from random import choice
from os import listdir

filelist = listdir('pics')

client = commands.Bot(command_prefix = '!')



@client.event
async def on_ready():
	print('bot is ready')

@client.event
async def on_member_join(member):
	print('{} зашёл на сервер'.format(member))


@client.event
async def on_member_remove(member):
	print('{} вышел в окно'.format(member))


@client.command()
async def hello(ctx):
	await ctx.send('ты што идиот??? Ты совсем жизнью контуженный? Зачем здороваться с роботом?')


@client.command(aliases=['постироничная_картинка'])
async def postpic(ctx):
	with open(f'pics/{choice(filelist)}', 'rb') as picture:
		file = discord.File(picture)

		await ctx.send(file=file)


client.run(str(os.environ.get('BOT_TOKEN')))