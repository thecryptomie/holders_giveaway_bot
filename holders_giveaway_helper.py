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

# Set up the style for logging output
logging.basicConfig(format='%(levelname)-4s '
                           '[%(module)s.%(funcName)s:%(lineno)d]'
                           ' %(message)s')

# instantiate the logger
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# _BOT_TOKEN = os.environ['BOT_TESTING']
_BOT_TOKEN = os.environ['ALIENTOURISM']

bot = commands.Bot(
    intents=discord.Intents.default()
)

class HoldersGiveaway(object):
    def __init__(self, config_file='./config.yaml'):
        self.project_dir = os.path.expanduser(
            '~/holders_giveaway_bot'
        )
        self.arc69_dir = os.path.join(
            self.project_dir, 'arc69_data'
        )
        self._holder_dir = os.path.join(
            self.project_dir, 'holder_data'
        )
        if config_file is None:
            LOG.error('Config file is required to run')
        else:
            with open(config_file, 'r') as fobj:
                self.config = yaml.safe_load(fobj)
        self.non_trait_cols = [
            'nft_name',
            'unit_name',
            'asa',
            'rank',
            'rarity_score',
            'creator'
        ]
        self.arc69_df = pd.read_csv(
            os.path.join(
                self.arc69_dir,
                self.config['arc69_data']
            ),
            header=0,
            index_col=None
        )

        self.trait_cols = [
            col for col in self.arc69_df.columns
            if col not in self.non_trait_cols
        ]

        self._holders_df = pd.read_csv(
            os.path.join(
                self._holder_dir,
                self.config['holder_data']
            ),
            header=0,
            index_col=None
        )
        # Merge the holders data with the arc69 data
        self._holders_df = pd.merge(
            self._holders_df,
            self._arc69_df,
            on='asa',
            how='inner',
            suffixes=('', '_1')
        )
        self._holders_df = self._holders_df.drop(
            columns=['unit_name_1']
        )
        # remove the wallets from the team members
        wallets_to_exclude = self.config['exclude_list']
        for wallet in wallets_to_exclude:
            LOG.info(f'Removing {wallet[:4]}...{wallet[-4:]} from holders dataframe')
            wallet_holdings = self._holders_df.groupby('address').get_group(
                wallet
            )
            self._holders_df.drop(index=wallet_holdings.index, inplace=True)

        self._N_tourists = self._holders_df.shape[0]
        self._unique_wallets = self.holders_df['address'].unique()

    @property
    def arc69_df(self):
        return self._arc69_df

    @arc69_df.setter
    def arc69_df(self, value):
        self._arc69_df = value

    @property
    def holders_df(self):
        """List of AGA holders"""
        return self._holders_df

    @holders_df.setter
    def holders_df(self, value):
        self._holders_df = value