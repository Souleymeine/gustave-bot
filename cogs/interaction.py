import discord
import random
from properties import Properties
from discord.ext import commands
from discord import app_commands

class Interaction(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.welcome_channel : discord.TextChannel = bot.get_channel(Properties.Channels.WELCOME_CHANNEL_ID)
    
    # ------------------------------EVENTS------------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        dm : discord.DMChannel = await self.bot.create_dm(user=member)
        await dm.send(Properties.Messages.welcome_message_dm())
        await self.welcome_channel.send(Properties.Messages.welcome_message_server().format(member.mention))
    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if (message.author == self.bot.user) : return
        # some cool features
        if (message.author.id == Properties.Users.DEV_ID):
            if (message.content.lower() == f"wesh {self.bot.user.mention}"):
                await message.reply("Wesh sousou")
            if (message.content.lower() == f"{self.bot.user.mention} check ça 🤜"):
                await message.reply(":left_facing_fist:")
            elif (message.content.lower() == f"{self.bot.user.mention} check ça 🤛"):
                await message.reply(":right_facing_fist:")


    # ------------------------------COMANDS------------------------------
    @app_commands.command(name="lovecalc_from_koya", description="Calcule le pourcenage de compatibilité")
    @app_commands.guild_only()
    async def lovecalc(self, interaction : discord.Interaction, user1 : discord.Member, user2 : discord.Member):
        if (user1 == user2):
            await interaction.response.send_message(content="Narcissique va !", ephemeral=True)
            return
        else :
            percentage : int = random.randint(0, 100)
            if (percentage in range(0, 20)):
                message = "\n## Impossible :broken_heart:"
            elif (percentage in range(20, 50)):
                message = "\n## Plutôt faible :blue_heart:"
            elif (percentage in range(50, 80)):
                message = "\n## Héhé ! :heart:"
            elif (percentage in range(80, 99)):
                message = "\n# Incroyable ! :heart_on_fire:"
            elif (percentage == 100):
                message = "\n# Un date s'impose."
            embed = discord.Embed(title=f"{percentage} %", description=f"{user1.mention} + {user2.mention}**__{message}__**", color=discord.Colour.purple())
            await interaction.response.send_message(embed=embed)
    # -------------------------------------------------------------------
    @app_commands.command(name="hug", description="Fait un calin à quelqu'un")
    @app_commands.guild_only()
    async def hug(self, interaction : discord.Interaction, user : discord.Member):
        if (user == self.bot.user):
            await interaction.response.send_message("Merci de penser un peu à moi :relaxed:", ephemeral=True)
        elif (user == interaction.user):
            await interaction.response.send_message("Ça va être compliqué...", ephemeral=True)
        else :
            embed = discord.Embed(description=f"## {user.mention}, **{interaction.user.mention} te fait un câlin** !", colour=discord.Colour.red())
            embed.set_image(url="https://media.tenor.com/Bo-NYTUVTp8AAAAC/love.gif")
            await interaction.response.send_message(embed=embed)
    # -------------------------------------------------------------------
    @app_commands.command(name="kiss", description="Fait un bisous à quelqu'un")
    @app_commands.guild_only()
    async def kiss(self, interaction : discord.Interaction, user : discord.Member):
        if (user == self.bot.user):
            await interaction.response.send_message("Ça ira tkt :hugging:", ephemeral=True)
        if (user == interaction.user):
            await interaction.response.send_message("Tu peux essayer de retourner tes lèvres mais ça va être chaud...", ephemeral=True)
        else :
            embed = discord.Embed(description=f"## {user.mention}, **{interaction.user.mention} te fait un bisous** !", colour=discord.Colour.red())
            embed.set_image(url="https://media.tenor.com/PS6medrGxqwAAAAd/cat-kiss.gif")
            await interaction.response.send_message(embed=embed)
    # -------------------------------------------------------------------
    @app_commands.command(name="bang", description="Tire sur quelqu'un")
    @app_commands.guild_only()
    async def bang(self, interaction : discord.Interaction, user : discord.Member):
        if (user == self.bot.user):
            await interaction.response.send_message("Wéééééésh :flushed:", ephemeral=True)
        elif (user == interaction.user):
            await interaction.response.send_message("Suicide :skull:\nhttps://media.tenor.com/ckWJMdNqny0AAAAC/wasted-putther.gif", ephemeral=True)
        else :
            embed = discord.Embed(description=f"## {user.mention}, **{interaction.user.mention} s'est levé·e ce matin et a choisi de te tirer dessus :skull:**", colour=discord.Colour.red())
            embed.set_image(url="https://media.tenor.com/3CGNudmJzP0AAAAC/barret-wallace-barret.gif")
            await interaction.response.send_message(embed=embed)
    # -------------------------------------------------------------------
    @app_commands.command(name="take_a_bite", description="Mords quelqu'un")
    @app_commands.guild_only()
    async def take_a_bite(self, interaction : discord.Interaction, user : discord.Member):
        if (user == self.bot.user):
            await interaction.response.send_message("C'est pas cool :sob:", ephemeral=True)
        elif (user == interaction.user):
            await interaction.response.send_message("https://media.tenor.com/yXt2_x_4VgoAAAAC/eren-jaeger-bitting-hand-eren-jaeger.gif", ephemeral=True)
        else :
            embed = discord.Embed(description=f"## {user.mention}, **{interaction.user.mention} te mords !**", colour=discord.Colour.red())
            embed.set_image(url="https://media.tenor.com/R_Oju0Tb-iUAAAAC/rip-bite.gif")
            await interaction.response.send_message(embed=embed)


async def setup(bot : commands.Bot):
    await bot.add_cog(Interaction(bot))
