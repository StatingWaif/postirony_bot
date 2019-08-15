import discord
from discord.ext import commands
from random import randint
import os
import vk
import aiohttp
from io import BytesIO
import wikipediaapi
from bs4 import BeautifulSoup as bs

async def pickingVkPic(ctx, url):
	session = vk.Session(access_token=str(os.environ.get('VK_TOKEN')))
	vk_api = vk.API(session, v='5.0')
	
	owner_id = url.split('/')[-1].replace('album', '').replace('_00', '') 

	photos = vk_api.photos.get(owner_id=owner_id, album_id='wall', rev=0, count=1000, photo_sizes=1)
	num_of_photos = photos['count']

	pic = randint(0, num_of_photos - 1)

	if pic > 999:
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
	bot_activity = discord.Activity(name='своих родителей( ͡° ͜ʖ ͡°) !help для списка команд', type=discord.ActivityType.listening)
	await client.change_presence(activity=bot_activity)

@client.event
async def on_member_join(member):
	print(f'{member} зашёл на сервер')


@client.event
async def on_member_remove(member):
	print(f'{member} вышел в окно')


@client.command(brief='Мягко указывает на то, что ты немного ошибаешься при приветствии', description='Тебе совсем нечем заняться? Просто используй команду. Зачем смотреть её полное описание... Дурак ржавый..')
async def hello(ctx):
	async with ctx.typing():
		await ctx.send('ты што идиот??? Ты совсем жизнью контуженный? Зачем здороваться с роботом?')


@client.command(aliases=['постироничная_картинка'], brief='присылает постироничную картинку', description='Ты тупой? Зачем тебе полное описание? Ты не понял, что было написано в команде !help? Ты идиот? Я тебя спрашиваю')
async def postpic(ctx):
	async with ctx.typing():
		await pickingVkPic(ctx, 'https://vk.com/album-162305728_00')	
		
@client.command(aliases=['папич', 'papichpic'], brief='присылает мем с папичем', descripiton='Полное описание для малолетних дебилов')
async def papapic(ctx):
    async with ctx.typing():
        await pickingVkPic(ctx, 'https://vk.com/album-181404250_00')
	
@client.command(brief='присылает полуголую бабищу', description='Присылает картинку с полуголой женщиной')
async def girlpic(ctx):
    async with ctx.typing():
        await pickingVkPic(ctx, 'https://vk.com/album-43234662_00')

@client.command(aliases=['что', 'определение'], brief='Команда + слово = определение этого слова', description='Присылает определение заданного слова из википедии')
async def what(ctx, *args):
    wiki_wiki = wikipediaapi.Wikipedia(language='ru', extract_format=wikipediaapi.ExtractFormat.HTML)

    page = ''

    for i in args:
        page += i + '_'

    page_py = wiki_wiki.page(page)
    if page_py.exists():
        soup = bs(page_py.summary, 'lxml')
            
        definition = soup.find('p').text
        await ctx.send(definition)
    else:
        await ctx.send('Такой страницы не существует ¯\_(ツ)_/¯')

client.run(str(os.environ.get('BOT_TOKEN')))
