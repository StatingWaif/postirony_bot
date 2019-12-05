import discord
from discord.ext import commands
import dbl
from random import randint, choice
import os
import vk
import aiohttp
from io import BytesIO
import wikipediaapi
from bs4 import BeautifulSoup as bs
import pyowm
import asyncio
import mysql.connector

border = '------------------------------------------'

class db:
	def __init__(self):
		original = str(os.environ.get('CLEARDB_DATABASE_URL')).replace('mysql://', '').replace('?reconnect=true', '')
		self.database = original.split('/')[-1]
		self.host = original.split('@')[-1].replace('/' + self.database, '')
		self.user = original.split(':')[0]
		self.passwd = original.split('@')[0].replace(self.user + ':', '')

		self.mydb = mysql.connector.connect(
			host=self.host,
			user=self.user,
			passwd=self.passwd,
			database=self.database,
			buffered=True
			)

	async def getInDataBase(self, group, pic):
		mycursor = self.mydb.cursor()
		try:
			mycursor.execute(f'INSERT INTO group_{group} VALUE ({pic})')
		except mysql.connector.errors.ProgrammingError:
			mycursor.execute(f"CREATE TABLE group_{group} (pic INTEGER(10))")
			mycursor.execute(f'INSERT INTO group_{group} VALUE ({pic})')
		self.mydb.commit()

	async def isInBase(self, group, pic):
		mycursor = self.mydb.cursor()
		listOfValues = []
		mycursor.execute(f'SELECT * FROM group_{group}')
		for value in mycursor:
			listOfValues.append(value[0])
		
		if pic in listOfValues:
			return True
		else:
			return False

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

		dBase = db()

		mycursor = dBase.mydb.cursor()
		group = owner_id.replace('-', '')

		try:
			mycursor.execute(f'SELECT * FROM group_{group}')
		except mysql.connector.errors.ProgrammingError:
			mycursor.execute(f'CREATE TABLE group_{group} (pic INTEGER(10))')

		while await dBase.isInBase(group, pic):
			pic = randint(0, num_of_photos - 1)
			
		offset = pic - (pic % 1000)
		photos = vk_api.photos.get(owner_id=owner_id, album_id='wall', rev=0, count=1000, photo_sizes=1, offset=offset)

		photo = photos['items'][pic - offset]['sizes'][-1]['src']

		async with aiohttp.ClientSession() as session:
			async with session.get(photo) as resp:
				if resp.status == 200:
					buffer = BytesIO(await resp.read())
					group = owner_id.replace('-', '')

					bufferfile = discord.File(buffer, filename=f'{group}_{pic}.jpg')
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
			print(border)
			print('Attempting to post server count')
			try:
				await self.dblpy.post_guild_count()
				print('Posted server count ({})'.format(self.dblpy.guild_count()))
			except Exception as e:
				print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
			await asyncio.sleep(1800)
			print(border)

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
	print(border)

@client.event
async def on_member_join(member):
	print(f'{member} зашел на сервер {member.guild.name}')

@client.event
async def on_member_remove(member):
    print(f'{member} вышел с сервера {member.guild.name} ')

@client.event
async def on_guild_join(guild):
	print(border)
	print(f'Теперь ещё и {guild.name}')
	print(border)

@client.event
async def on_guild_remove(guild):
	print(border)
	print(f'Прощай, {guild.name}')
	print(border)

@client.command(brief='Мягко указывает на то, что ты немного ошибаешься при приветствии', description='Тебе совсем нечем заняться? Просто используй команду. Зачем смотреть её полное описание... Дурак ржавый..')
async def hello(ctx):
	async with ctx.typing():
		author = ctx.message.author
		await ctx.send(f'{author.mention} ты што идиот??? Ты совсем жизнью контуженный? Зачем здороваться с роботом?')


@client.command(aliases=['постироничная_картинка'], brief='Присылает постироничную картинку', description='Ты тупой? Зачем тебе полное описание? Ты не понял, что было написано в команде !help? Ты идиот? Я тебя спрашиваю')
async def postpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-162305728_00')
	
@client.command()
async def schoolpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-185340181_00')

@client.command()
async def agrpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-184764992_00')

@client.command()
async def kindpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-184003532_00')

@client.command()
async def villpic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-186137194_00')

@client.command()
async def rompic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-184394012_00')
		
@client.command(aliases=['папич', 'papichpic'], brief='Присылает мем с папичем', descripiton='Полное описание для малолетних дебилов')
async def papapic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-181404250_00')

@client.command()
async def gachipic(ctx):
	await pickingVkPic(ctx, 'https://vk.com/album-73192688_00')
	
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

	description = f'Температура: {temp}° \n \
	Статус: {status} \n \
	Скорость ветра: {windSpeed} м/с'

	embed = discord.Embed(title=city, colour=discord.Colour.green(), description=description)

	await ctx.send(embed=embed)

@client.command()
async def blacklist(ctx):
	if (ctx.message.author.discriminator == '3191' and ctx.message.author.name == 'StatingWaif') or (ctx.message.author.discriminator == '2726' and ctx.message.author.name == 'Rendei<3'):
		channel = ctx.message.channel

		async for message in channel.history(limit=5):
			if message.author.discriminator == '2560' and message.author.bot == True and message.author.name == 'Постироничная шелупонь':
				file_name = message.attachments[0].filename
				group = file_name.split('_')[0]
				pic_num = file_name.split('_')[1].replace('.jpg', '')

				dBase = db()

				await dBase.getInDataBase(group, pic_num)
				break
		animals = [':gorilla:', ':dog:', ':pig:', ':cow:', ':koala:', ':frog:', ':boar:', ':monkey_face:', ':panda_face:']
		await ctx.send(f'Ваше пожелание будет исполнено{choice(animals)} ')
		print('blacklisted')

@client.command()
async def help(ctx):
	embed = discord.Embed(title='Список команд для использования бота', colour=discord.Colour.green())
	postValue = '\
	**!postpic** - классическая картинка\n \
	**!kindpic** - добрая картинка \n \
	**!rompic** - романтичная картинка для общения с дамами \n \
	**!agrpic** - агрессивная картинка \n \
	**!schoolpic** - школьная картинка \n \
	**!villpic** - деревенская картинка \n \
	'

	otherValue = '\
	**!gachipic** - гачимучи картинка\n \
	**!memepic** - english meme\n \
	**!papapic** - несмешная картинка с папичем\n \
	**!girlpic** - картинка с полуголой женщиной(**NSFW**) \
	'

	notPicValue = '\
	**!help** - список команд \n \
	**!hello** - поздороваться с ботом\n \
	**!weather** + **город** = погода в этом городе\n \
	**!what** + **слово** = определение этого слова \
	'

	embed.add_field(name='Команды для постироничных картинок:', value=postValue)
	embed.add_field(name='Команды для других картинок:', value = otherValue)
	embed.add_field(name='Остальные команды:', value=notPicValue)
	await ctx.send(embed=embed)
	
client.run(str(os.environ.get('BOT_TOKEN')))
