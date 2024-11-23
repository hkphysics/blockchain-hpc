#!/usr/bin/env python

"""Tests for `quantlib_server` package."""

import pytest
from pydantic import BaseModel
import pydantic_core
import pydantic_quantlib as pql


from quantlib_server import quantlib_server

def test_ql():
    payoff = pql.PlainVanillaPayoff(type=pql.OptionType.Put, strike=40)
    european_exercise = pql.EuropeanExercise(date=pql.Date(d=4, m=1, y=2022))
    european_option = pql.VanillaOptionBase(payoff=payoff, exercise=european_exercise)
    qleo = european_option.to_quantlib()
    dump = european_option.model_dump()
    print(dump)
    obj1 = {"VanillaOptionBase": dump}
    a = [getattr(pql, k).model_validate(v) for k, v in obj1.items()]

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')

def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
