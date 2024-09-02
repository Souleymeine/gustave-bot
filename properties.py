import random
from datetime import datetime, timedelta
import pytz

class Properties():
    GUILD_ID : int = 1082719753572974672
    SERVER_LINK : str = "https://discord.gg/6xjQYECJDs"
    DATE_AND_TIME_IN_FRANCE : datetime = datetime.now(pytz.timezone("Etc/GMT-2"))
    FRANCE_TIME_OFFSET : timedelta = pytz.timezone("Etc/GMT-2").utcoffset(dt=None)
    
    class Users():
        ADMIN_ID = 877556326149021717
        DEV_ID = 877556326149021717

    class Roles():
        MUTE_ROLE_ID : int = 1084065540227727461
        STAFF_ROLE_ID : int = 1086348343950712832
        VERIFIED_ROLE_ID : int = 1086350698456813639
    
    class FilePaths():
        JSON_WARN_PATH : str = r"data\warns.json"
        JSON_SWEARWORDS_PATH : str = r"data\swearwords.json"
    
    class Moderation():
        CHANCES_BEFORE_MUTING : int = 3
    
    class Channels():
        ALERT_CHANNEL_ID : int = 1095696971114750015
        WELCOME_CHANNEL_ID : int = 1083459294978130010
        ANNOUNCMENT_CHANNEL_ID : int = 1104809789726412830
        RULES_CHANNEL_ID : int = 1123241208844656731
    
    class Messages():
        def token_grab_alert_message() -> str:
            """The fisrt value has to be formated as "user.mention", the second as "message.channel.mention" and the third as "time"\n-> Properties.Messages.TOKEN_GRAB_ALERT_MESSAGE.format(user.mention, message.channel.mention, time)"""
            message_list = ["**Ton attention est requise, cher admin/modo**,\n\n{0} a envoyé un lien suspect dans {1} ({2}). Sûrement un bot ou quelqu'un qui s'est fait hacké.\nJ'ai donc muté l'utilisateur en question, cependant il se peut que je me soit trompé. Vérifie donc s'il n'y a pas eu erreur de ma part et unmute le avec `/unmute` si c'est le cas.\n\nC'est tout pour moi, passe une bonne journée soldat !"]
            return random.choice(message_list)
        def obscene_language_alert_message() -> str:
            """The fisrt value has to be formated as "user.mention", the second as "message.channel.mention" and the third as "time"\n-> Properties.Messages.TOKEN_GRAB_ALERT_MESSAGE.format(user.mention, message.channel.mention, time)"""
            message_list = ["Juste au cas où,\n\n{0} vient d'envoyé des insultes dans {1} ({2})\nHésite pas à checker les logs si tu veux voir les messages que j'ai supprimé\n\nVoili voilou…"]
            return random.choice(message_list)
        def too_many_warns_alert_message() -> str:
            """The fisrt value has to be formated as "user.mention", the second as "time" and the third as Properties.Moderation.CHANCES_BEFORE_MUTING"\n-> Properties.Messages.TOKEN_GRAB_ALERT_MESSAGE.format(user.mention, time, Properties.Moderation.CHANCES_BEFORE_MUTING)"""
            message_list : str = ["À titre informatif,\n\n{0} a été muté à l'instant ({1}).\nIl cumule un total de **{2}** warns.\nJe te laisse décider ce que tu fera de lui/elle.\n\nBonne journée soldat!"]
            return random.choice(message_list)
       
        def spam_dm_message() -> str:
            return "Je viens ici pour t'informer que tu as été temporairement mute pour 10 minutes.\n\n**Fait attention à ce que tu fais, car la prochaine pourrait être un mute ou un ban définitif**.\nComporte toi mieux, s'il te plaît"
        def welcome_message_dm() -> str:
            message_list = [f"Salut, je suis Gustave. Je suis envoyé par le Staff d'Epsylium pour te donner quelques informations avant que tu puisses profiter du serveur discord.\nAprès avoir lu et accepté notre règlement et avoir vérifié que tu possédais bien le rôle de sécurité @VERIFIED, les salons <#{Properties.Channels.WELCOME_CHANNEL_ID}> et <#{Properties.Channels.RULES_CHANNEL_ID}> sont présents sur le discord pour que tu puisses comprendre correctement le fonctionnement de notre communauté.\nLe salon <#{Properties.Channels.ANNOUNCMENT_CHANNEL_ID}> est aussi présent, il est essentiel, les infos importantes seront écrites dans celui-ci. Tu peux aussi être mis au courant quand nous recherchons des personnes pour intégrer le staff. Nous te laisserons ensuite discuter librement dans les salons dédiés, en te souhaitant, un très bon moment sur Épsylium.\n\nCordialement, @CA2E"]
            return random.choice(message_list)
        def welcome_message_server() -> str:
            """The first value has to be formated as user.mention -> Properties.Messages.welcome_message_server.format(user.mention)"""
            message_list = ["**{0} a rejoint le serveur ! :sunglasses:**", "Hello {0}, soit le/la bienvenu·e :)", "Salut {0}! Soit le/la bienvenu·e ;)"]
            return random.choice(message_list)