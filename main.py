import discord
import random
from discord.ext import commands

# Set up the bot with the required intents
intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.members = True  # Ensure we have access to member information

bot = commands.Bot(command_prefix="!", intents=intents)

def is_allowed_user(user_id):
    try:
        with open('allowed_ids.txt', 'r') as file:
            allowed_ids = [line.strip() for line in file.readlines()]
        return str(user_id) in allowed_ids
    except Exception as e:
        print(f"Error reading allowed_ids.txt: {str(e)}")
        return False

# Function to generate a random color
def random_color():
    return discord.Color(random.randint(0x000000, 0xFFFFFF))

# Global dictionary to store role mappings per guild
role_dicts = {}

# Load roles from a text file, create them in the server, and send a message with reactions
@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def create_roles(ctx):
    try:
        with open('roles.txt', 'r') as file:
            roles = [role.strip() for role in file.readlines() if role.strip()]

        role_message_template = "Wybierz grupę ćwiczeniową:\n\n"
        emoji_list = [
            "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🔶",
            "🔷", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🔺", "🔻", "⬛",
            "⬜", "⭐", "🌟", "✨", "⚡", "🔥", "💧", "🌈", "🌙", "☀️",
            "🍎", "🍊", "🍌", "🍉", "🍇", "🍓", "🍈", "🥭", "🌽", "🍅",
        ]
        # Check if roles exceed the number of emojis
        if len(roles) > len(emoji_list):
            await ctx.send("Za mało emoji. Maksymalna liczba ról to 40.")
            return

        created_roles = []
        message_ids = []  # To store message IDs

        # Create roles and messages in batches of 20
        for i in range(0, len(roles), 20):
            role_batch = roles[i:i+20]
            role_message = role_message_template

            created_roles_batch = []
            for index, role_name in enumerate(role_batch):
                role = await ctx.guild.create_role(name=role_name, color=random_color())
                created_roles_batch.append(role)
                created_roles.append(role)

                # Add role to the message
                role_message += f"{emoji_list[index]} - {role_name}\n"

            # Send the role message
            role_msg = await ctx.send(role_message)
            message_ids.append(role_msg.id)

            # Add reactions for each role
            for index in range(len(role_batch)):
                await role_msg.add_reaction(emoji_list[index])

            # Initialize role_dict for this guild if it doesn't exist
            if ctx.guild.id not in role_dicts:
                role_dicts[ctx.guild.id] = {}

            # Define a dictionary to map reactions to roles
            role_dicts[ctx.guild.id].update({emoji_list[index]: created_roles_batch[index] for index in range(len(role_batch))})

        # Save the message IDs to edit later
        with open('message_ids.txt', 'w') as msg_file:
            msg_file.write('\n'.join(map(str, message_ids)))

        # Define a check function to ensure reactions are from users, not the bot
        def check(reaction, user):
            return user != bot.user and str(reaction.emoji) in role_dicts[ctx.guild.id]

        # Wait for reactions and assign/remove roles based on reactions
        while True:
            reaction, user = await bot.wait_for('reaction_add', check=check)
            role = role_dicts[ctx.guild.id][str(reaction.emoji)]
            member = ctx.guild.get_member(user.id)

            # Add role if user reacts
            if role not in member.roles:
                await member.add_roles(role)
                await ctx.send(f"Dodano {role.name} dla {user.mention}.")
            
            # Wait for unreact event to remove the role
            @bot.event
            async def on_reaction_remove(reaction, user):
                if user != bot.user and str(reaction.emoji) in role_dicts[ctx.guild.id]:
                    role = role_dicts[ctx.guild.id][str(reaction.emoji)]
                    member = ctx.guild.get_member(user.id)
                    if role in member.roles:
                        await member.remove_roles(role)
                        await ctx.send(f"Usunięto role {role.name} role dla {user.mention}.")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")


# Command to delete roles using their IDs
@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def delete_roles(ctx):
    try:
        with open('role_ids.txt', 'r') as file:
            role_ids = [line.strip() for line in file.readlines()]

        for role_id in role_ids:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
            if role:
                await role.delete()
                await ctx.send(f"Usunięto role: {role.name}")

        # Clear the role_ids.txt file after deleting roles
        with open('role_ids.txt', 'w') as file:
            file.write("")

        with open('message_id.txt', 'r') as msg_file:
            message_id = int(msg_file.read())

        role_msg = await ctx.fetch_message(message_id)

        await role_msg.delete()

        await ctx.send("Usunięto wszystkie role i wiadomość.")

        with open('message_id.txt', 'w') as msg_file:
            msg_file.write("")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")


# Command to add a single role and update the message
@bot.command()
@commands.check(lambda ctx: is_allowed_user(ctx.author.id))
@commands.has_permissions(manage_roles=True)
async def add_role(ctx, role_name):
    try:
        with open('roles.txt', 'a') as file:
            file.write(f"{role_name}\n")

        # Create the new role
        role = await ctx.guild.create_role(name=role_name, color=random_color())

        # Get the message ID and edit it
        with open('message_id.txt', 'r') as msg_file:
            message_id = int(msg_file.read())

        role_msg = await ctx.fetch_message(message_id)

        emoji_list = [
            "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🔶",
            "🔷", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🔺", "🔻", "⬛",
            "⬜", "⭐", "🌟", "✨", "⚡", "🔥", "💧", "🌈", "🌙", "☀️",
        ]

        # Get the number of roles already created
        with open('role_ids.txt', 'r+') as role_id_file:
            role_ids = role_id_file.readlines()
            if len(role_ids) >= len(emoji_list):
                await ctx.send("Za mało emoji. Maksymalna liczba ról to 30.")
                return
            role_id_file.write(f"{role.id}\n")

        # Add the role to the message
        new_emoji = emoji_list[len(role_ids)]
        updated_message = role_msg.content + f"\n{new_emoji} - {role_name}\n"
        await role_msg.edit(content=updated_message)

        # Add the new reaction
        await role_msg.add_reaction(new_emoji)

        # Update the role dictionary
        if ctx.guild.id not in role_dicts:
            role_dicts[ctx.guild.id] = {}
        role_dicts[ctx.guild.id][new_emoji] = role

        await ctx.send(f"Rola {role_name} została dodana i przypisana do {new_emoji}.")

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")


# Bot token (replace with your actual bot token)
#read from token.private
with open('token.private', 'r') as file:
    token = file.read().strip()
bot.run(token)
