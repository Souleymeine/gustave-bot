import discord
import json
from properties import Properties
from discord import app_commands
from discord.ext import commands
from discord.utils import get
from discord.ui import ChannelSelect, Button, View, Select

class Commands(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        
        # Temporary variables (act like placeholders)----------
        self.is_waiting_for_sending_message : bool = False
        self.is_waiting_for_role_message : bool = False
        self.request_sending_message : discord.Message = None
        self.request_role_message : discord.Message = None
        self.send_message_option : dict = {"embed" : False, "channel" : None, "message" : None, "requester" : None}
        self.role_message_option : dict = {"embed" : False, "message" : None, "requester" : None, "roles" : {}} # <-- {reaction : role}
        # -----------------------------------------------------

        self.guild : discord.Guild = bot.get_guild(Properties.GUILD_ID)
        self.muted_role : discord.Role = self.guild.get_role(Properties.Roles.MUTE_ROLE_ID)

    class SendMessageDropDownView(View):
        def __init__(self, bot : commands.Bot):
            super().__init__()

            self.bot = bot
            self.command_cog = self.bot.get_cog("Commands")

            self.timeout = 120

            self.channel_select = ChannelSelect(channel_types=[discord.ChannelType.text], placeholder="Séléctionne un salon", row=0)
            self.channel_select.callback = self.channel_select_callback

            self.message_type_select = Select(options=[
                discord.SelectOption(
                    label="Message classique",
                    emoji="📄",
                    description="Message normal, comme tous les autres.",
                    value="classique"), 
                discord.SelectOption(
                    label="Message \"embed\"", 
                    emoji="✉️", 
                    description="Message encadré, de la même manière que l'entête ☝️.",
                    value="embed")], 
                placeholder="Choisi un type de message", row=1)
            self.message_type_select.callback = self.message_type_select_callback
            
            next_button = Button(label="Continuer", style=discord.ButtonStyle.green, row=2)
            next_button.callback = self.next_button_callback
            cancel_button = Button(label="Annuler", style=discord.ButtonStyle.red, row=2)
            cancel_button.callback = self.cancel_button_callback
            
            self.add_item(self.channel_select)
            self.add_item(self.message_type_select)
            self.add_item(next_button)
            self.add_item(cancel_button)

        async def channel_select_callback(self, interaction : discord.Interaction):
            await interaction.response.defer()
            msg = await interaction.original_response()
            if (len(self.message_type_select.values) == 0):
                embed = discord.Embed(title="Séléctionne maintenant un type de message", color=discord.Colour.orange())
            else :
                embed = discord.Embed(title="Appuie maintenant sur \"Continuer\"", color=discord.Colour.green())
            await msg.edit(embed=embed)
        async def message_type_select_callback(self, interaction : discord.Interaction):
            await interaction.response.defer()
            msg = await interaction.original_response()
            if (len(self.channel_select.values) == 0):
                embed = discord.Embed(title="Séléctionne maintenant un salon", color=discord.Colour.orange())
            else :
                embed = discord.Embed(title="Appuie maintenant sur \"Continuer\"", color=discord.Colour.green())
            await msg.edit(embed=embed)
        async def next_button_callback(self, interaction : discord.Interaction):
            await interaction.response.defer()
            msg = await interaction.original_response()

            if (len(self.channel_select.values) == 0):
                embed = discord.Embed(title="Séléctionne un salon !", color=discord.Colour.red())
            elif (len(self.message_type_select.values) == 0):
                embed = discord.Embed(title="Séléctionne un type de message !", color=discord.Colour.red())
            else : 
                embed = discord.Embed(title="Enfin, écrit ce que tu veux envoyer en répondant à ce message", 
                    description=f"Il sera automatiquement envoyé après confirmation\n*Tu peux toujours modifier les paramètres ci-dessous après avoir cliqué sur \"Continuer\"*\n\n***Salon séléctionné : {self.channel_select.values[0].mention}\nType {self.message_type_select.values[0]}***",
                    color=discord.Colour.blurple())
                
                is_embed = True if self.message_type_select.values[0] == "embed" else False

                # configure data
                self.command_cog.is_waiting_for_sending_message = True
                self.command_cog.send_message_option["embed"] = is_embed
                self.command_cog.send_message_option["channel"] = await self.channel_select.values[0].fetch()
                self.command_cog.send_message_option["requester"] = interaction.user

            await msg.edit(embed=embed)
        async def cancel_button_callback(self, interaction : discord.Interaction):
            await interaction.response.defer()
            await interaction.delete_original_response()
            self.command_cog.cancel_sending_command()

    def cancel_sending_command(self):
        self.is_waiting_for_sending_message = False
        self.request_sending_message = None
        self.send_message_option : dict = {"embed" : False, "channel" : None, "message" : None, "requester" : None}

    def reset_logs(self, member : discord.Member, interaction : discord.Interaction):
        with (open(Properties.FilePaths.JSON_WARN_PATH, "r", encoding="utf-8") as json_file):
            json_list : list = json.load(json_file)

        # logs format :
        data: dict = {
        "name": str(member._user),
        "id" : member.id,
        "forgived by": f"{str(interaction.user._user)} (using /unmute)",
        "at": str((interaction.created_at + Properties.FRANCE_TIME_OFFSET)),
        "warn": 0}

        with open(Properties.FilePaths.JSON_WARN_PATH, "w", encoding="utf-8") as json_file:
            json_list.append(data)
            json.dump(json_list, json_file, ensure_ascii=False, indent=4)
    
    
    # ------------------------------EVENTS------------------------------
    async def confirm_button_callback(self, interaction : discord.Interaction):  
        await interaction.response.defer()
        
        if (self.send_message_option["embed"] == False):
            await self.send_message_option["channel"].send(self.send_message_option["message"])
        else :
            embed = discord.Embed(description=self.send_message_option["message"])
            await self.send_message_option["channel"].send(embed=embed)
        
        embed = discord.Embed(title="C'est fait ✅", description=self.send_message_option["channel"].mention + " :eyes:")
        await interaction.channel.send(content=self.send_message_option["requester"].mention, embed=embed)
        
        await self.request_sending_message.delete()
        self.cancel_sending_command()
        
        messages = [msg async for msg in self.bot.get_channel(interaction.channel_id).history(limit=20)]
        reply : discord.Message = get(messages, id=interaction.message.reference.message_id)
        
        await reply.delete()
        await interaction.delete_original_response()
    async def cancel_button_callback(self, interaction : discord.Interaction):
        await interaction.response.defer()
        
        await self.request_sending_message.delete()
        self.cancel_sending_command()
        
        messages = [msg async for msg in self.bot.get_channel(interaction.channel_id).history(limit=20)]
        reply : discord.Message = get(messages, id=interaction.message.reference.message_id)
        
        await reply.delete()
        await interaction.delete_original_response()
        
        await interaction.channel.send("D'acc :thumbsup:", delete_after=5)

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if (self.is_waiting_for_sending_message and message.reference != None):
            if (message.reference.message_id == self.request_sending_message.id):
                confirm_button = Button(label="Confirmer", style=discord.ButtonStyle.danger, row=0)
                confirm_button.callback = self.confirm_button_callback
                cancel_button = Button(label="Annuler", style=discord.ButtonStyle.gray, row=0)
                cancel_button.callback = self.cancel_button_callback
                
                view = View()
                view.add_item(confirm_button)
                view.add_item(cancel_button)
                
                self.send_message_option["message"] = message.content

                type = "embed" if self.send_message_option["embed"] else "classic"
                channel : discord.TextChannel = self.send_message_option["channel"]
                
                embed = discord.Embed(title="Tu veux envoyer ce message ?", 
                    description=f"\n**__Rappel :__** message **{type}**, dans **{channel.mention}**", 
                    color=discord.Colour.red())
                await message.reply(embed=embed, view=view)
    @commands.Cog.listener()
    async def on_message_delete(self, message : discord.Message):
        # if there is a message we're waiting for
        if (self.request_sending_message != None and self.is_waiting_for_sending_message):
            if (message == self.request_sending_message):
                self.cancel_sending_command()


    # ------------------------------COMANDS------------------------------
    @app_commands.command(name="clear", description="Supprime un nombre de message précisé d'une traite")
    @app_commands.guild_only()
    async def clear(self, interaction : discord.Interaction, amount : int):
        # error handling
        if (amount < 1):
            await interaction.response.send_message("Ton nombre de message doit être supérieur à 1 !", ephemeral=True)
            return
        
        if (amount > 1):
            interaction_message = f"{amount} messages ont été supprimé"
        elif (amount == 1) :
            interaction_message = f"{amount} message a été supprimé"

        await interaction.response.send_message(interaction_message, ephemeral=True)
        await interaction.channel.purge(limit=amount)
    # -------------------------------------------------------------------
    @app_commands.command(name="mute", description="Mute le l'utilisateur ciblé")
    @app_commands.guild_only()
    async def mute(self, interaction : discord.Interaction, member : discord.Member, reason : str=""):
        # error handling
        if (member == self.bot.user):
            lmao_emoji : discord.Emoji = get(self.guild.emojis, name="ptdrr")
            await interaction.response.send_message(f"Bien tenté {lmao_emoji}", ephemeral=True)
            return
        elif (self.muted_role in member.roles):
            await interaction.response.send_message(f"{member.mention} est déjà muté", ephemeral=True)
            return
        
        # embed
        title : str = "__Membre muté__"
        color : discord.Colour = discord.Colour.red()
        profile_picture : str = member.display_avatar.url
        if (reason == ""):
            embed_message = discord.Embed(color=color, title=title, description=f"**{member.mention}** a été muté")
        else :
            embed_message = discord.Embed(color=color, title=title, description=f"**{member.mention}** a été muté pour la raison suivante : ||{reason}||")
        embed_message.set_thumbnail(url=profile_picture)
        
        await interaction.response.send_message(embed=embed_message)
        
        await member.add_roles(self.muted_role)
    # -------------------------------------------------------------------
    @app_commands.command(name="unmute", description="Unmute le l'utilisateur ciblé")
    @app_commands.guild_only()
    async def unmute(self, interaction : discord.Interaction, member : discord.Member):
        # error handling
        if (member == self.bot.user):
            await interaction.response.send_message(f"Je ne peux pas être muté, <@{Properties.Users.DEV_ID}> te passe 50 balles si t'y arrives :eyes:", ephemeral=True)
            return
        elif (self.muted_role not in member.roles):
            await interaction.response.send_message(f"{member.mention} n'est pas muté", ephemeral=True)
            return

        # embed
        title : str = "__Membre unmuté__"
        color : discord.Colour = discord.Colour.blue()
        profile_picture : str = member.display_avatar.url
        embed_message = discord.Embed(color=color, title=title, description=f"**{member.mention}** a été unmuté, profite bien de ton retour parmis nous :partying_face: !\n||~~et ne fais plus de bêtises surtout~~||")
        embed_message.set_thumbnail(url=profile_picture)
        
        await interaction.response.send_message(embed=embed_message)
        
        self.reset_logs(member=member, interaction=interaction)
        await member.remove_roles(self.muted_role)
    # -------------------------------------------------------------------
    @app_commands.command(name="send", description="envoie un message via Gustave")
    @app_commands.guild_only()
    async def send(self, interaction : discord.Interaction):
        embed = discord.Embed(title="Choisi d'abord le salon dans lequel tu veux que j'envoie le message",
            color=discord.Colour.blurple())
        view = self.SendMessageDropDownView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)
        self.request_sending_message = interaction.channel.last_message
    # -------------------------------------------------------------------
    @app_commands.command(name="addswear", description="Ajoute une insulte à la liste des mots interdis")
    @app_commands.guild_only()
    async def addswear(self, interaction : discord.Interaction, swear : str):
        with open(Properties.FilePaths.JSON_SWEARWORDS_PATH, "r", encoding="utf-8") as json_file:
            json_list = json.load(json_file)
            if swear not in json_list:
                json_list.append(swear)
                print(f"added : \"{swear}\" to the swear word list")
                await interaction.response.send_message(f"le mot ||{swear}|| a bien été ajouté à la liste des mots bannis.", ephemeral= True)
            else:
                print(f"the word \"{swear}\" is already in the list")
                await interaction.response.send_message(f"le mot ||{swear}|| fait déjà partie de la liste des mots bannis.", ephemeral= True)
        
        with open(Properties.FilePaths.JSON_SWEARWORDS_PATH, "w", encoding="utf-8") as json_file:
            data = json.dumps(json_list, ensure_ascii=False)
            json_file.write(data)
    # -------------------------------------------------------------------
    @app_commands.command(name="removeswear", description="Retire une insulte à la liste des mots interdis")
    @app_commands.guild_only()
    async def removeswear(self, interaction : discord.Interaction, swear : str):
        with open(Properties.FilePaths.JSON_SWEARWORDS_PATH, "r", encoding="utf-8") as json_file:
            json_list = json.load(json_file)
            if swear not in json_list:
                print(f"not found : \"{swear}\" doesn't exist in the swear words list")
                await interaction.response.send_message(f"le mot ||{swear}|| n'existe pas dans la liste des mots bannis.", ephemeral= True)
            else:
                json_list.remove(swear)
                print(f"the word \"{swear}\" was succesfully removed from the swear wrods list")
                await interaction.response.send_message(f"le mot ||{swear}|| a été supprimé de la liste des mots bannis.", ephemeral= True)
        
        with open(Properties.FilePaths.JSON_SWEARWORDS_PATH, "w", encoding="utf-8") as json_file:
            data = json.dumps(json_list, ensure_ascii=False)
            json_file.write(data)
    # -------------------------------------------------------------------
    @app_commands.command(name="ping", description="Indique la latence du bot")
    @app_commands.guild_only()
    async def ping(self, interaction : discord.Interaction):
        embed = discord.Embed(title=f"Pong ! {self.bot.latency*1000}ms")  
        await interaction.response.send_message(embed=embed)

async def setup(bot : commands.Bot):
    await bot.add_cog(Commands(bot))