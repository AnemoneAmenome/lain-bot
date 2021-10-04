import discord, os, random, asyncio, logging, statistics, json, math, sys, traceback
from discord.ext import commands
logger = logging.getLogger(__name__)

from modules.core.resources import Resources

from modules.services.anilist.enums import ScoreFormat, Status
from modules.services.models.user import UserStatus
from modules.services import Service

class Misc(commands.Cog, name="other"):
	"""Probably one-off or WIPs"""

	def __init__(self, bot):
		self.bot = bot

	async def cog_command_error(self, ctx, err):
		logger.exception("Error during command")
		if isinstance(err, discord.ext.commands.errors.CommandInvokeError):
			err = err.original
		try:
			if isinstance(err, discord.ext.commands.MissingPermissions):
				await ctx.send("You lack the needed permissions!")
			elif isinstance(err, Anilist2.AnilistError):
				if err.status == 404:
					await ctx.send('https://files.catbox.moe/b7drrm.jpg')
					await ctx.send('*no results*')
				else:
					await ctx.send(f"Query request failed\nmsg: {err.message}\nstatus: {err.status}")	
			elif isinstance(err, HTTPError):	
				await ctx.send(err.http_error_msg)
			else:
				await ctx.send('error!', file=discord.File(os.getcwd() + '/assets/lain_err_sm.png'))
		except:
			pass
		
	@commands.command()
	async def compatibility(self, ctx, *args):
		"""See your compatiblity with other registered users"""
		kind = "anime"
		if args and args[0] == "manga":
			kind = "manga"

		channel = ctx.message.channel
		guild = ctx.guild

		await ctx.send("I am slow at this for now. Just wait")
		# await ctx.trigger_typing()

		user = await Resources.user_col.find_one(
			{'discord_id': str(ctx.author.id)},
			{
				'service': 1,
				'profile.name': 1,
				'profile.score_format': 1,
				f"lists.{kind}": 1,
			}
		)
		if not user:
			return await ctx.send("Can't do compare. You're not registered")

		# get all users in db that are in this guild
		userIdsInGuild = [str(u.id) for u in guild.members if u.id != ctx.author.id]
		users = [d async for d in Resources.user_col.find(
			{
				'discord_id': {'$in': userIdsInGuild},
				'status': { '$not': { '$eq': UserStatus.INACTIVE } },      
			},
			{
				'service': 1,
				'profile.name': 1,
				'profile.score_format': 1,
				f"lists.{kind}": 1,
			}
			)
		]
		# await ctx.trigger_typing()

		scores = []
		for u in users:
			scores.append((u['profile']['name'], _get_comp_score(user, u, kind)))
		scores.sort(key=lambda e: e[1][0])

		# remove empty
		scores = [score for score in scores if score[1][0]]

		if scores:
			# embed text to output
			embed = discord.Embed(
				title = f"{ctx.author.display_name}'s {kind} compatibility scores",
				description = "The lower the score the more compatible",
				color = discord.Color.blue(),
			)

			for score in scores:
				embed.add_field(name=score[0], value=f"{round(score[1][0], 3)} ({score[1][1]})", inline=True)

			await ctx.send(embed=embed)
		else:
			await ctx.send("No compatibilities. Most likely didn't share any scores with anyone")

def _get_comp_score(u1, u2, kind):
	try:
		with open(os.getcwd()+'/assets/data/mal2al.json', 'r') as f:
			mal2al = json.load(f)

		with open(os.getcwd()+'/assets/data/al2mal.json', 'r') as f:
			al2mal = json.load(f)

		av1 = 0
		av2 = 0
		combined = []
		for i in u1['lists'][kind]:
			e = u1['lists'][kind][i]
			ii = [i]
			if u1['service'] == Service.ANILIST and u2['service'] == Service.MYANIMELIST:
				if i in al2mal[kind]:
					ii = al2mal[kind][i]
				else:
					ii = []
			if u1['service'] == Service.MYANIMELIST and u2['service'] == Service.ANILIST:
				if i in mal2al[kind]:
					ii = mal2al[kind][i]
				else:
					ii = []
			for s in ii:
				s = str(s)
				if s != None and s != "None" and s in u2['lists'][kind]:
					sf1 = ScoreFormat(u1['profile']['score_format'])
					sf2 = ScoreFormat(u2['profile']['score_format'])
					s1 = sf1.normalized_score(e['score'])
					s2 = sf2.normalized_score(u2['lists'][kind][s]['score'])
					# print(f"{u1['profile']['name']} x {u2['profile']['name']} -- {i} : {s} :: {type(s1)}[{s1}] {type(s2)}[{s2}]")
					if not s1 or not s2:
						continue
					combined.append((s1, s2))
					av1 = av1 + s1
					av2 = av2 + s2

		av1 = av1/len(combined)
		av2 = av2/len(combined)

		sdv1 = 0
		sdv2 = 0
		for c in combined:
			sdv1 = sdv1 + ((c[0] - av1)**2)
			sdv2 = sdv2 + ((c[1] - av2)**2)
		sdv1 = math.sqrt(sdv1/(len(combined)-1))
		sdv2 = math.sqrt(sdv2/(len(combined)-1))

		diff = 0
		for c in combined:
			diff = diff + abs( ((c[0] - av1)/sdv1) - ((c[1] - av2)/sdv2) )
		return (diff/len(combined), len(combined))
	except Exception as e:
		print(sys.exc_info())
		traceback.print_exc()
		return (0,0)
