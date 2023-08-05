# coding=utf-8
from functools import partial
from random import random
import Pyro4
from pyage.core import address

from pyage.core.stop_condition import StepLimitStopCondition
from pyage_forams.solutions.distributed.neighbour_matcher import Neighbour2dMatcher
from pyage_forams.solutions.agent.remote_aggegate import create_remote_agent
from pyage_forams.solutions.distributed.request import create_dispatcher
from pyage_forams.solutions.environment import environment_factory, Environment2d
from pyage_forams.solutions.foram import create_forams
from pyage_forams.solutions.genom import GenomFactory
from pyage_forams.solutions.insolation_meter import InsolationMeter
from pyage_forams.solutions.statistics import SimpleStatistics


factory = GenomFactory(chambers_limit=5)
genom_factory = lambda: factory.generate
forams = create_forams(1, initial_energy=5)
agents = partial(create_remote_agent, "A" + str(random()))
insolation_meter = InsolationMeter
size = lambda: 3

environment = environment_factory(regeneration_factor=0.1, clazz=Environment2d)
neighbour_matcher = Neighbour2dMatcher

request_dispatcher = create_dispatcher()

stop_condition = lambda: StepLimitStopCondition(90)

reproduction_minimum = lambda: 10
movement_energy = lambda: 0.25
growth_minimum = lambda: 10

address_provider = address.SequenceAddressProvider
stats = SimpleStatistics

ns_hostname = lambda: "127.0.0.1"
pyro_daemon = Pyro4.Daemon()
daemon = lambda: pyro_daemon