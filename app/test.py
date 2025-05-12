#!/usr/bin/env python3

"""
NOTE: Test the simulator locally. First build the `queries` binary with `cargo build --release` and then run this script.
"""

from modsim import data
from simulator import Simulator
from store import QRangeStore

store = QRangeStore()
sim = Simulator(store, data)
sim.simulate()
print(f"{len(store)=}")
