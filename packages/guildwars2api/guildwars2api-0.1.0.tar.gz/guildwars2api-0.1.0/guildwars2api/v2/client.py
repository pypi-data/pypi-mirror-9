# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from guildwars2api.base import BaseClient
from .resources import (
    Item,
    Recipe,
    RecipeSearch,
    Skin,
    Continent,
    Floor,
    Map,
    Listing,
    Exchange,
    Price,
    Build,
    Color,
    File,
    Quaggan,
    World,
)


class GuildWars2API(BaseClient):

    base_url = "https://api.guildwars2.com/v2"

    def __init__(self, user_agent='Guild Wars 2 Python API Wrapper'):
        super(GuildWars2API, self).__init__(user_agent=user_agent)

        self.items = self._register(Item)
        self.recipes = self._register(Recipe)
        self.recipes_search = self._register(RecipeSearch)
        self.skins = self._register(Skin)
        self.continents = self._register(Continent)
        self.floors = self._register(Floor)
        self.maps = self._register(Map)
        self.listings = self._register(Listing)
        self.exchange = self._register(Exchange)
        self.prices = self._register(Price)
        self.build = self._register(Build)
        self.colors = self._register(Color)
        self.files = self._register(File)
        self.quaggans = self._register(Quaggan)
        self.worlds = self._register(World)

    def _register(self, resource):
        return resource(self.host, self.session)
