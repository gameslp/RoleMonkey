import asyncio
import json
import os
import discord
import random
from discord.ext import commands
# Global dictionary to store role mappings per guild
role_dicts = {}

# Set up the bot with the required intents
intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.members = True  # Ensure we have access to member information

bot = commands.Bot(command_prefix="!", intents=intents)

emoji_list = [
            "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🔶",
            "🔷", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🔺", "🔻", "⬛",
            "⬜", "⭐", "🌟", "✨", "⚡", "🔥", "💧", "🌈", "🌙", "☀️",
            "🍎", "🍊", "🍌", "🍉", "🍇", "🍓", "🍈", "🥭", "🌽", "🍅",
]

with open("images.txt", "r") as file:
    images = [line.strip() for line in file.readlines()]

with open("malpy.json", encoding="utf-8") as file:
    malpy = json.load(file)["malpy"]

def log(message):
    with open("logs.txt", "a") as file:
        file.write(f"{message}\n")

def is_allowed_user(user_id):
    try:
        with open('allowed_ids.txt', 'r') as file:
            allowed_ids = [line.strip() for line in file.readlines()]
        return str(user_id) in allowed_ids
    except Exception as e:
        print(f"Error reading allowed_ids.txt: {str(e)}")
        return False

def random_color():
    return discord.Color(random.randint(0x000000, 0xFFFFFF))

async def create_roles_fun(ctx, roles):
    existing_roles = ctx.guild.roles
    created_roles = []
    rate = 1
    for role_name in roles:
        if rate % 3 == 0:
            log(f"Czekam 5 sekund...")
            await asyncio.sleep(5)
        role = None
        for existing_role in existing_roles:
            if existing_role.name == role_name:
                role = existing_role
                break
        if role:
            log(f"Rola już istnieje: {role_name}")
            created_roles.append(role)
        else:
            log(f"Tworzenie roli: {role_name}")
            role = await ctx.guild.create_role(name=role_name, color=random_color())
            rate += 1
            created_roles.append(role)
    return created_roles

@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def stworz_role(ctx):
    try:
        args = ctx.message.content.split(" ")[1:]

        if len(args) != 1:
            await ctx.send("Użycie: !stworz_role <angielski/cwiczenia/wykladowe>")
            return
        
        await ctx.send("Tworzę role... (~1min)")

        if args[0] == "angielski":
            with open('roles_angielski.txt', 'r') as file:
                roles_angielski = [role.strip() for role in file.readlines() if role.strip()]
            created_roles_angielski = await create_roles_fun(ctx, roles_angielski)
            with open("role_angielski_ids.txt", "w") as file:
                file.write("\n".join([str(role.id) for role in created_roles_angielski]))

        if args[0] == "cwiczenia":
            with open('roles_cwiczenia.txt', 'r') as file:
                roles_cwiczenia = [role.strip() for role in file.readlines() if role.strip()]
            created_roles_cwiczenia = await create_roles_fun(ctx, roles_cwiczenia)
            with open("role_cwiczenia_ids.txt", "w") as file:
                file.write("\n".join([str(role.id) for role in created_roles_cwiczenia]))
        if args[0] == "wykladowe":
            with open('roles_wykladowe.txt', 'r') as file:
                roles_wykladowe = [role.strip() for role in file.readlines() if role.strip()]
            created_roles_wykladowe = await create_roles_fun(ctx, roles_wykladowe)
            with open("role_wykladowe_ids.txt", "w") as file:
                file.write("\n".join([str(role.id) for role in created_roles_wykladowe]))

        await ctx.send("Role zostały utworzone.")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

async def sendRoles(rolesIds, ctx, role_message_template):
    for i in range(0, len(rolesIds), 20):
        role_batch = rolesIds[i:i+20]
        role_message = ""

        for index, role_id in enumerate(role_batch):
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
            role_message += f"{emoji_list[index]} - {role.name}\n"
        title = ""
        if i == 0:
            title = role_message_template
        embed = discord.Embed(title=title, description=role_message, color=random_color())
        embed.set_thumbnail(url=random.choice(images))

        role_msg = await ctx.send(embed=embed)

        for index in range(len(role_batch)):
            await role_msg.add_reaction(emoji_list[index])

        if role_msg.id not in role_dicts:
            role_dicts[role_msg.id] = {}

        role_dicts[role_msg.id].update({emoji_list[index]: discord.utils.get(ctx.guild.roles, id=int(role_id)) for index, role_id in enumerate(role_batch)})

        # with open("message_ids.txt", "a") as file:
        #     file.write(f"{role_msg.id}\n")

    return role_dicts

@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def wyslij_role(ctx):
    try:

        # with open("message_ids.txt", "r") as file:
        #     message_ids = [int(line.strip()) for line in file.readlines()]
        #     for message_id in message_ids:
        #         role_msg = await ctx.fetch_message(message_id)
        #         await role_msg.delete()
        # with open("message_ids.txt", "w") as file:
        #     file.write("")
            
        with open("role_angielski_ids.txt", "r") as file:
            role_ids_angielski = [int(line.strip()) for line in file.readlines()]

        with open("role_cwiczenia_ids.txt", "r") as file:
            role_ids_cwiczenia = [int(line.strip()) for line in file.readlines()]

        with open("role_wykladowe_ids.txt", "r") as file:
            role_ids_wykladowe = [int(line.strip()) for line in file.readlines()]
        
        role_message_template_angielski = "Wybierz swoją grupę angielski:\n"
        role_message_template_cwiczenia = "Wybierz swoją grupę ćwiczeniową:\n"
        role_message_template_wykladowe = "Wybierz swoją grupę wykładową:\n"

        role_dicts = await sendRoles(role_ids_angielski, ctx, role_message_template_angielski)
        role_dicts = await sendRoles(role_ids_cwiczenia, ctx, role_message_template_cwiczenia)
        role_dicts = await sendRoles(role_ids_wykladowe, ctx, role_message_template_wykladowe)

        def check(reaction, user):
            return user != bot.user and str(reaction.emoji) in role_dicts[reaction.message.id]

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def wyczysc_kanal(ctx):
    try:
        if ctx.channel.id == 1292113551674179595 or ctx.channel.id == 1292593060487761950:
            # with open("message_ids.txt", "w") as file:
            #     file.write("")
            await ctx.channel.purge()
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

# Command to delete roles using their IDs
@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def usun_role(ctx):
    try:
        await ctx.send("Usuwam role... (~30s)")
        with open("role_angielski_ids.txt", "r") as file:
            role_ids_angielski = [int(line.strip()) for line in file.readlines()]

        with open("role_cwiczenia_ids.txt", "r") as file:
            role_ids_cwiczenia = [int(line.strip()) for line in file.readlines()]

        with open("role_wykladowe_ids.txt", "r") as file:
            role_ids_wykladowe = [int(line.strip()) for line in file.readlines()]

        roles_ids = role_ids_angielski + role_ids_cwiczenia + role_ids_wykladowe

        for role_id in roles_ids:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
            if role:
                await role.delete()
                log(f"Usunięto role: {role.name}")

        with open("role_angielski_ids.txt", "w") as file:
            file.write("")

        with open("role_cwiczenia_ids.txt", "w") as file:
            file.write("")
        
        with open("role_wykladowe_ids.txt", "w") as file:
            file.write("")

        log("Role zostały usunięte.")

        await ctx.send("Role zostały usunięte.")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

#read from token.private
with open('token.private', 'r') as file:
    token = file.read().strip()

@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def wyslij_malpy(ctx):
    try:
        for malpa in malpy:
            embed = discord.Embed(title=malpa["name"], color=random_color())
            embed.set_thumbnail(url=malpa["image"])
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('✔️')
            if msg.id not in role_dicts:
                role_dicts[msg.id] = {}

            role_dicts[msg.id].update({'✔️': discord.utils.get(ctx.guild.roles, id=int(malpa["test_id"]))})
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.event
async def on_reaction_add(reaction, user):
    message_id = reaction.message.id
    if message_id in role_dicts:
        if user != bot.user and str(reaction.emoji) in role_dicts[reaction.message.id]:
            role = role_dicts[reaction.message.id][str(reaction.emoji)]
            member = reaction.message.guild.get_member(user.id)

            if role not in member.roles:
                await member.add_roles(role)

@bot.event
async def on_reaction_remove(reaction, user):
    message_id = reaction.message.id
    if message_id in role_dicts:
        role = role_dicts[reaction.message.id][str(reaction.emoji)]
        member = reaction.message.guild.get_member(user.id)

        if role in member.roles:
            await member.remove_roles(role)

bot.run(token)