import discord
from discord.ext import commands

description = '''Test'''

class Client:

	serverID = 0

	prefix = "k!"
	bot = commands.Bot(command_prefix=prefix, description=description) #sets up the bot

	# @bot.check
	# async def check_serverID(ctx):
		# global serverID
		# Client.serverID = ctx.guild.id
		# print('Global check complete! Server ID: '+str(Client.serverID))
		# return Client.serverID
