from collections import Counter
import pandas as pd
import logging
import os
import random
import yaml
import discord
from discord.ext import commands, pages
import numpy as np
from numpy.random import default_rng
import requests

from holders_giveaway_helper import HoldersGiveaway

# Set up the style for logging output
logging.basicConfig(format='%(levelname)-4s '
                           '[%(module)s.%(funcName)s:%(lineno)d]'
                           ' %(message)s')

# instantiate the logger
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

_BOT_TOKEN = os.environ['BOT_TESTING']
# _BOT_TOKEN = os.environ['ALIENTOURISM']

bot = commands.Bot(
    intents=discord.Intents.all()
)

_HOLDERS_DATA = HoldersGiveaway(config_file='./config.yaml')

async def admin_check(ctx):
    admin_role_id = _HOLDERS_DATA.config['admin_role']
    # if the user has the project's admin role, it will return it
    # other wise it returns none
    role = ctx.author.get_role(admin_role_id)
    if isinstance(role, discord.Role):
        return True
    else:
        return False

@bot.slash_command(
    name='wallet_info',
    description='List the NFTs held by the wallet'
)

async def wallet_holdings(
        ctx,
        wallet
):
    await ctx.defer()
    holder_df = _HOLDERS_DATA.holders_df
    wallet_str = f'{wallet[:4]}...{wallet[-4:]}'
    try:
        holdings = holder_df.groupby('address').get_group(wallet)
    except KeyError as e:
        LOG.info('Wallet not found')
        await ctx.respond(f'{wallet_str} not found in holders data')
        return

    embed = discord.Embed(
        title=f'{wallet_str} Holdings',
        description=(
            f'**Number of Tourists Held:** {holdings.shape[0]}\n'
            f'**Odds of Winning:** {holdings.shape[0]/_HOLDERS_DATA._N_tourists:0.3%}'
        )
    )
    await ctx.respond(embeds=[embed])

@bot.slash_command(
    name='giveaway',
    description='Holders giveaway'
)
@commands.check(admin_check)
async def giveaway(ctx):
    await ctx.defer(ephemeral=False)
    embed = discord.Embed(
        title='Giveaway',
        description='Holders only giveaway!'
    )
    holder_df = _HOLDERS_DATA.holders_df
    wallet_str = holder_df['address'].apply(
        lambda val: f'{val[:4]}...{val[-4:]}'
    )
    holder_df['address_short'] = wallet_str
    nfts_per_holder = Counter(wallet_str)
    # first wallet is creators wallet
    holders_to_show = 15
    top_5 = nfts_per_holder.most_common(holders_to_show)
    holder_str = ''
    for i, (key, val) in enumerate(top_5):
        holder_str += f'{i+1:0.0f}) {key}, {val}\n'
    embed.add_field(
        name=f'Top {holders_to_show:0.0f} Holders',
        value=holder_str
    )
    await ctx.respond(embeds=[embed])

    # Create an array of holder wallets where each holder's wallet shows up
    # once for each NFT they hold.
    entries = []
    for address, count in nfts_per_holder.items():
        entries += [address] * count

    # shuffle the entries list around to mix up the order
    random.shuffle(entries)

    # Choose a winner
    winner = random.choice(entries)

    winner_info = holder_df[holder_df['address_short'] == winner]
    embed=discord.Embed(
        title='Winning Wallet',
    )
    count = winner_info.shape[0]
    embed.add_field(
        name='Address',
        value=winner_info["address"].iloc[0],
        inline=False
    )
    embed.add_field(
        name='Tourist Holdings',
        value=count,
        inline=False
    )
    await ctx.send(embeds=[embed])

@giveaway.error
async def giveaway_error(ctx, error):
    await ctx.respond('Command is open to admins only', ephemeral=True)

if __name__ == "__main__":
    bot.run(_BOT_TOKEN)
