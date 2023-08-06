#!/usr/bin/env python
import json
import sys

from pyquanta import Quanta

if __name__ == "__main__":
    quanta = Quanta(url='http://localhost:3000/api')
    with open(sys.argv[1]) as creds:
        quanta.connect(*creds.read().rstrip().split())
    quanta.use_site(7)
    scenario = quanta.scenarios.all()[0]
    print(scenario.name)
    scenario.Step.create(no=42, name="toto", url='https://toto.com')
    print(list(map(lambda s: s.name, scenario.steps)))
