import discord
from discord.ext import commands
from random import choice, randint
import os
import vk
import aiohttp
from io import BytesIO
from math import ceil

async def pickingVkPic(ctx):
	session = vk.Session(access_token=str(os.environ.get('VK_TOKEN')))
	vk_api = vk.API(session, v='5.0')

	url = 'https://vk.com/album-162305728_00'
	owner_id = url.split('/')[-1].replace('album', '').replace('_00', '') 

	photos = vk_api.photos.get(owner_id=owner_id, album_id='wall', rev=0, count=1000, photo_sizes=1)
	num_of_photos = photos['count']

	pic = randint(0, num_of_photos - 1)

	if pic > 1000:
		offset = pic - (pic % 1000)
		photos = vk_api.photos.get(owner_id=owner_id, album_id='wall', rev=0, count=1000, photo_sizes=1, offset=offset)

		photo = photos['items'][pic - offset]['sizes'][-1]['src']
	else:
		photo = photos['items'][pic]['sizes'][-1]['src']

	async with aiohttp.ClientSession() as session:
		async with session.get(photo) as resp:
			if resp.status == 200:
				buffer = BytesIO(await resp.read())
				bufferfile = discord.File(buffer, filename='pic.jpg')
				await ctx.send(file=bufferfile)


	

client = commands.Bot(command_prefix = '!')




@client.event
async def on_ready():
	print('bot is ready')
	await client.change_presence(activity=discord.Game('( ͡° ͜ʖ ͡°) !help для команд'))

@client.event
async def on_member_join(member):
	print(f'{member} зашёл на сервер')


@client.event
async def on_member_remove(member):
	print(f'{member} вышел в окно')


@client.command()
async def hello(ctx, brief='Мягко указывает на то, что ты немного ошибаешься при приветствии', description='Тебе совсем нечем заняться? Просто используй команду. Зачем смотреть её полное описание... Дурак ржавый..'):
	await ctx.send('ты што идиот??? Ты совсем жизнью контуженный? Зачем здороваться с роботом?')


@client.command(aliases=['постироничная_картинка'], brief='посылает постироничную картинку', description='Ты тупой? Зачем тебе полное описание? Ты не понял, что было написано в команде !help? Ты идиот? Я тебя спрашиваю')
async def postpic(ctx):
	await pickingVkPic(ctx)
				
	
	
	

client.run(str(os.environ.get('BOT_TOKEN')))
