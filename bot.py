import discord
from discord.ext import commands
import dbl
from random import randint
import os
import vk
import aiohttp
from io import BytesIO
import wikipediaapi
from bs4 import BeautifulSoup as bs
import pyowm
import asyncio

async def sendVk(message):
	session = vk.Session(access_token=str(os.environ.get('SEND_TOKEN')))
	vk_api = vk.API(session, v='5.45')
	vk_api.messages.send(domain=str(os.environ.get('NAME_SEND')), message=message, random_id=randint(0, 1000000000))

async def pickingVkPic(ctx, url):
	async with ctx.typing():
		session = vk.Session(access_token=str(os.environ.get('VK_TOKEN')))
		vk_api = vk.API(session, v='5.0')

		owner_id = url.split('/')[-1].replace('album', '').replace('_00', '') 

		photos = vk_api.photos.get(owner_id=owner_id, album_id='wall', rev=0, count=1000, photo_sizes=1)
		num_of_photos = photos['count']

		pic = randint(0, num_of_photos - 1)

		directory = owner_id.replace('-', '')

		with open(f'blacklist/{directory}.txt') as blacklist:

			while str(pic) in blacklist.read():
				pic = randint(0, num_of_photos - 1)

		offset = pic - (pic % 1000)
		photos = vk_api.photos.get(owner_id=owner_id, album_id='wall', rev=0, count=1000, photo_sizes=1, offset=offset)

		photo = photos['items'][pic - offset]['sizes'][-1]['src']

		async with aiohttp.ClientSession() as session:
			async with session.get(photo) as resp:
				if resp.status == 200:
					buffer = BytesIO(await resp.read())

					owner_id = owner_id.replace('-', '')

					bufferfile = discord.File(buffer, filename=f'{owner_id}_{pic}.jpg')
					await ctx.send(file=bufferfile)	
					print(pic)
					

client = commands.Bot(command_prefix = '!')
client.remove_command('help')

class DiscordBotsOrgAPI(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.token = str(os.environ.get('DBL_TOKEN'))
		self.dblpy = dbl.DBLClient(self.bot, self.token)
		self.updating = self.bot.loop.create_task(self.update_stats())

	async def update_stats(self):
		while not self.bot.is_closed():
			print('Attempting to post server count')
			try:
				await self.dblpy.post_guild_count()
				print('Posted server count ({})'.format(self.dblpy.guild_count()))
			except Exception as e:
				print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
			await asyncio.sleep(1800)

def setup(bot):
	bot.add_cog(DiscordBotsOrgAPI(bot))

setup(client)

@client.event
async def on_ready():
	print('bot is ready')
	bot_activity = discord.Activity(name='своих родителей !help для списка команд', type=discord.ActivityType.listening)
	await client.change_presence(activity=bot_activity)
	guilds = client.guilds
	servers = []

	for guild in guilds:
		servers.append(guild.name)

	message = f'Кол-во серверов: {len(guilds)}. \n' + ', '.join(servers) + '.'
	await sendVk(message)

@client.event
async def on_member_join(member):
	print(f'{member} зашел на сервер')

@client.event
async def on_member_remove(member):
    try:
        print(f'{member} вышел с сервера')
        nameOfMember = member.nick
        if nameOfMember == None:
            nameOfMember = member
        leftMessage = f'**{nameOfMember} вышел с сервера :cry:**'
        textChannels = member.guild.text_channels

        if len(textChannels) == 1:
            await textChannels[0].send(leftMessage)
        elif len(textChannels) > 1:
            channel = discord.utils.get(textChannels, name='основной')
            if channel == None:
                channel = discord.utils.get(textChannels, name='general')
                if channel == None:
                    channel = textChannels[0]
            await channel.send(leftMessage)
    except discord.errors.Forbidden:
        print('remove forbidden')

@client.command(brief='Мягко указывает на то, что ты немного ошибаешься при приветствии', description='Тебе совсем нечем заняться? Просто используй команду. Зачем смотреть её полное описание... Дурак ржавый..')
async def hello(ctx):
	async with ctx.typing():
		author = ctx.message.author
		await ctx.send(f'{author.mention} ты што идиот??? Ты совсем жизнью контуженный? Зачем здороваться с роботом?')


@client.command(aliases=['постироничная_картинка'], brief='Присылает постироничную картинку', description='Ты тупой? Зачем тебе полное описание? Ты не понял, что было написано в команде !help? Ты идиот? Я тебя спрашиваю')
async def postpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-162305728_00')	
		
@client.command(aliases=['папич', 'papichpic'], brief='Присылает мем с папичем', descripiton='Полное описание для малолетних дебилов')
async def papapic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-181404250_00')

@client.command()
async def musicpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-187034124_00')
	
@client.command(brief='Присылает полуголую бабищу', description='Присылает картинку с полуголой женщиной')
async def girlpic(ctx):
	try:
		if ctx.channel.is_nsfw() == True:
			await pickingVkPic(ctx, 'https://vk.com/album-43234662_00')
		else:
			await ctx.send('Канал должен быть **NSFW**  ¯\_(ツ)_/¯')
	except AttributeError:
		await ctx.send('Используйте эту команду только в **NSFW** канале')
@client.command()
async def memepic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-150550417_00')

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

@client.command(aliases=['погода'], brief='Команда + город = погода в этом городе', description='Присылает погоду в заданном городе')
async def weather(ctx, city):
	owm = pyowm.OWM(str(os.environ.get('PYOWM_TOKEN')), language='ru')
	observation = owm.weather_at_place(city)
	w = observation.get_weather()
	temp = int(w.get_temperature('celsius')['temp'])

	if int(temp) > 0:
		temp = '+' + str(temp)
	status = w.get_detailed_status()
	windSpeed = w.get_wind()['speed']

	await ctx.send(f'Место: {city}\nТемпература: {temp}°\nСтатус: {status}\nСкорость ветра: {windSpeed} м/с')

@client.command()
async def blacklisted(ctx):
	if ctx.message.author.discriminator == '3191' and ctx.message.author.name == 'StatingWaif':
		channel = ctx.message.channel
		async for message in channel.history(limit=5):
			if message.author.discriminator == '2560' and message.author.bot == True and message.author.name == 'Постироничная шелупонь':
				file_name = message.attachments[0].filename
				group = file_name.split('_')[0]
				pic_num = file_name.split('_')[1].replace('.jpg', '')

				with open (f'blacklist/{group}.txt', 'a+') as tf:
					if not pic_num in tf.read():
						tf.write(pic_num + '\n')
						break

@client.command()
async def help(ctx):
	author = ctx.message.author
	description='**!hello** - поздороваться с ботом\n**!postpic** - присылает постироничную картинку\n**!papapic** - присылает несмешную картинку с папичем\n**!girlpic** - присылает картинку с полуголой бабищей(**NSFW**)\n**!memepic** - присылает english meme**\n!weather** + **город** = погода в этом городе\n**!what** + **слово** = определение этого слова'

	embed = discord.Embed(title='Список команд для использования бота', description=description, colour=discord.Colour.green())
	await author.send(embed=embed)
	
client.run(str(os.environ.get('BOT_TOKEN')))
