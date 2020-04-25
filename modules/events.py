import discord
from discord.ext import commands

from .client import Client
from .config import Config
from .safebooru import Safebooru

bot = Client.bot
game = discord.Game("with her phone") #sets the game the bot is currently playing

class Events:
	
	@bot.event
	async def on_ready(): #bot startup event
		print('Kotori-san is ready to go!')
		await bot.change_presence(status=discord.Status.online, activity=game)
		
		channel = bot.get_channel(Config._botChannel)
		
		safebooruImageURL = Safebooru.booruSearch('otonashi_kotori 1girl')
		
		embed = discord.Embed(
			title = 'こんにちは、プロデューサーさん！',
			description = 'Kotori is now online!',
			color = discord.Color.green()
		)
		
		embed.set_image(url=safebooruImageURL)
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/avatar.png')
			
		await channel.send(embed=embed)