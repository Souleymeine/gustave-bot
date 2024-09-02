import discord
import json
import re
from urlextract import URLExtract
from properties import Properties
from enum import Enum
from datetime import timedelta
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

        self.guild : discord.Guild = bot.get_guild(Properties.GUILD_ID)
        self.mute_role : discord.Role = bot.get_guild(Properties.GUILD_ID).get_role(Properties.Roles.MUTE_ROLE_ID)
        self.staff_role : discord.Role = bot.get_guild(Properties.GUILD_ID).get_role(Properties.Roles.STAFF_ROLE_ID)
        self.alert_channel : discord.TextChannel = bot.get_channel(Properties.Channels.ALERT_CHANNEL_ID)
        self.antispam = commands.CooldownMapping.from_cooldown(5, 13, commands.BucketType.member)
        self.too_many_violation = commands.CooldownMapping.from_cooldown(4, 7, commands.BucketType.member)
    
    class Reasons(Enum):
        OBSCENE_LANGUAGE = "language obscène"
        TOKEN_GRAB = "tentative de token grab"
        SPAM = "spam"
        TOO_MANY_WARNS = "seuil de warn dépassé"

    def is_swearword(self, word : str) -> bool:
        with (open(Properties.FilePaths.JSON_SWEARWORDS_PATH, "r", encoding="utf-8") as json_file):            
            swear_list : list = json.load(json_file)
            if (word.lower() in swear_list):
                return True
            else :
                return False
    def contains_sus_link(self, message : discord.Message) -> bool:
        splited_message = re.split(';|,|:|/|//|\|\\\\|\(|\)| ', message.content)
        discord_com_link = "discord.com"
        urls_in_message : list = [URLExtract().find_urls(text=item)[0] for item in splited_message if len(URLExtract().find_urls(item)) != 0]
        if (len(urls_in_message) > 0):
            for link in urls_in_message:
                if ("discord" in link and link != discord_com_link):
                    print(f"{link} potential token grabing link detected!")
                    return True
                else :
                    return False

    def get_warn_count(self, member : discord.Member) -> int :
        with open(Properties.FilePaths.JSON_WARN_PATH, "r", encoding="utf-8") as json_file:
        # JSON FILE HAS TO BE A LIST, AT LEAST AN EMPTY ONE --> "[]"
            json_list : list = json.load(json_file)
            id_key: str = "id"
            member_dictionaries = [dictionary for dictionary in json_list if dictionary.get(id_key) == member.id]

            #if we found somthing
            if len(member_dictionaries) > 0:
                last_dict: dict = member_dictionaries[len(member_dictionaries) - 1]
                member_warn_count: int = last_dict.get("warn")
            #or if this member isn't warn
            else :
                member_warn_count = 0
        
        return member_warn_count
    def write_warn_logs(self, message : discord.Message, reason : Reasons):
        with (open(Properties.FilePaths.JSON_WARN_PATH, "r", encoding="utf-8") as json_file):
            json_list : list = json.load(json_file)
            id_key: str = "id"
            member_dictionaries = [dictionary for dictionary in json_list if dictionary.get(id_key) == message.author.id]
            # if we found somthing
            if len(member_dictionaries) != 0:
                last_dict: dict = member_dictionaries[len(member_dictionaries) - 1]
                member_warn_count: int = last_dict.get("warn")
                member_warn_count += 1
            # or if it's the first time
            else :
                member_warn_count = 1

        # json logs format :
        if (reason == self.Reasons.OBSCENE_LANGUAGE or reason == self.Reasons.TOO_MANY_WARNS):
            data_swear: dict = {
            "name": str(message.author._user),
            "id": message.author.id,
            "message": message.content,
            "channel": message.channel.name,
            "at": str((message.created_at + Properties.FRANCE_TIME_OFFSET).strftime("%d/%m/%Y %H:%M:%S")),
            "warn": member_warn_count}
            json_list.append(data_swear)
        elif (reason == self.Reasons.SPAM):
            data_spam: dict = {
            "name": str(message.author._user),
            "id": message.author.id,
            "last_spamed_message" : message.content,
            "last_message_link": message.jump_url,
            "channel": message.channel.name,
            "at": str((message.created_at + Properties.FRANCE_TIME_OFFSET).strftime("%d/%m/%Y %H:%M:%S")),
            "warn": member_warn_count}
            json_list.append(data_spam)

        # write data in the json file
        with open(Properties.FilePaths.JSON_WARN_PATH, "w", encoding="utf-8") as json_file:
            json.dump(json_list, json_file, ensure_ascii=False, indent=4)

    async def send_alert(self, reason : Reasons, message : discord.Message):
        admin : discord.Member = await self.bot.fetch_user(Properties.Users.ADMIN_ID)
        time : str = str((message.created_at + Properties.FRANCE_TIME_OFFSET).strftime("%Hh%M"))
        self.write_warn_logs(message=message, reason=reason)

        match reason:
            case self.Reasons.TOKEN_GRAB:
                dm_message = Properties.Messages.token_grab_alert_message().format(message.author.mention, message.channel.mention, time)
                embed = discord.Embed(title=f"Un membre a été muté", description=f"{message.author.mention} a été muté, raison : **{reason.value}**", colour=discord.Colour.red())
                await message.author.add_roles(self.mute_role)
            case self.Reasons.OBSCENE_LANGUAGE:
                dm_message = Properties.Messages.obscene_language_alert_message().format(message.author.mention, message.channel.mention, time)
                embed = discord.Embed(title=f"Un membre a été warn", description=f"{message.author.mention} a été warn, raison : **{reason.value}**", colour=discord.Colour.orange())
                embed.add_field(name="warns :", value=f"**{str(self.get_warn_count(member=message.author))}**")
            case self.Reasons.SPAM:
                embed = discord.Embed(title=f"Un membre a été muté temporairement", description=f"{message.author.mention} a été privé de parole, raison : **{reason.value}**", colour=discord.Colour.red())
                embed.add_field(name="warns :", value=f"**{str(self.get_warn_count(member=message.author))}**")
            case self.Reasons.TOO_MANY_WARNS:
                dm_message  = Properties.Messages.too_many_warns_alert_message().format(message.author.mention, time, Properties.Moderation.CHANCES_BEFORE_MUTING)
                embed = discord.Embed(title=f"Un membre a été muté", description=f"{message.author.mention} a été muté, raison : **{reason.value}**", colour=discord.Colour.red())
                embed.add_field(name="warns :", value=f"**{str(self.get_warn_count(member=message.author))}** (max)")
                await message.author.add_roles(self.mute_role)

        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="Dans :", value=f"**{message.channel.mention}**")
        await self.alert_channel.send(f"**{self.staff_role.mention}**", embed=embed)
        try :
            dm : discord.DMChannel = await admin.create_dm()
            await dm.send(dm_message)
        except :
            pass
    
    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if (message.author == self.bot.user) : return
        
        # anti-spam (Big thanks to this guy : https://youtu.be/799hRjPiEeQ)
        bucket = self.antispam.get_bucket(message=message)
        retry_after = bucket.update_rate_limit()
        if (retry_after):
            await message.delete()
            await message.channel.send(f"**Doucement {message.author.mention}, doucement !**", delete_after=7)
            violations = self.too_many_violation.get_bucket(message=message)
            check = violations.update_rate_limit()
            if (check and not message.author.is_timed_out()):
                await message.author.timeout(timedelta(minutes=10), reason=self.Reasons.SPAM.value)
                await self.send_alert(reason=self.Reasons.SPAM, message=message)
                try : await message.author.send(Properties.Messages.spam_dm_message())
                except : pass

        # moderation
        world_list : str = message.content.split(" ")

        if (self.contains_sus_link(message=message)):
            await self.send_alert(message=message, reason=self.Reasons.TOKEN_GRAB)

        for i in range(len(world_list)):
            if (self.is_swearword(world_list[i])):
                if (self.get_warn_count(member=message.author) < Properties.Moderation.CHANCES_BEFORE_MUTING):
                    await self.send_alert(message=message, reason=self.Reasons.OBSCENE_LANGUAGE)
                else:
                    await message.author.add_roles(self.mute_role)
                    await self.send_alert(message=message, reason=self.Reasons.TOO_MANY_WARNS)
                await message.reply(":face_with_raised_eyebrow:")
                await message.delete()


async def setup(bot : commands.Bot):
    await bot.add_cog(Moderation(bot))