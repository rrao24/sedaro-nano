# SIMULATOR

from functools import reduce
from operator import __or__
import subprocess
import json

from modsim import agents
from store import QRangeStore

def parse_query(query):
    # NOTE: The query parser is invoked via a subprocess call to the Rust binary
    popen = subprocess.Popen('../queries/target/release/sedaro-nano-queries', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    (stdout, stderr) = popen.communicate(query)
    if popen.returncode:
        raise Exception(f"Parsing query failed: {stderr}")
    return json.loads(stdout)

class Simulator:
    """
    A Simulator is used to simulate the propagation of agents in the universe.
    This class is *not* pure. It mutates the data store in place and maintains internal state.

    It is given an initial state of the following form:
    ```
    {
        'agentId': {
            'time': <time of instantiation>,
            'timeStep': <time step for propagation>,
            **otherSimulatedProperties,
        },
        **otherAgents,
    }
    ```

    Args:
        store (QRangeStore): The data store in which to save the simulation results.
        init (dict): The initial state of the universe.
    """

    def __init__(self, store: QRangeStore, init: dict):
        # NOTE: Creating a Simulator object does all the simulation "building"
        self.store = store
        store[-999999999, 0] = init
        self.init = init
        self.times = {agentId: state["time"] for agentId, state in init.items()}
        self.sim_graph = {}
        for (agentId, sms) in agents.items():
            agent = []
            for sm in sms:
                consumed = parse_query(sm["consumed"])["content"]
                produced = parse_query(sm["produced"])
                func = sm["function"]
                agent.append({"func": func, "consumed": consumed, "produced": produced})
            self.sim_graph[agentId] = agent

    def read(self, t):
        try:
            data = self.store[t]
        except IndexError:
            data = []
        return reduce(__or__, data, {}) # combine all data into one dictionary

    def step(self, agentId, universe):
        """Run an Agent for a single step."""
        state = dict()
        sms = []
        for sm in self.sim_graph[agentId]:
            sms.append((agentId, sm))
        while sms:
            next_sms = []
            for (agentId, sm) in sms:
                if self.run_sm(agentId, sm, universe, state) is None:
                    next_sms.append((agentId, sm))
            if len(sms) == len(next_sms):
                raise Exception(f"No progress made while evaluating statemanagers for agent {agentId}. Remaining statemanagers: {[sm["func"].__name__ for (agentId, sm) in sms]}")
            sms = next_sms
        return state

    def run_sm(self, agentId, sm, universe, newState):
        """Run a State Manager for a single step."""
        inputs = []
        for q in sm["consumed"]:
            found = self.find(agentId, q, universe, newState)
            if found is None:
                return None
            inputs.append(found)
        res = sm["func"](*inputs)
        self.put(agentId, sm["produced"], universe, newState, res)
        return res

    def find(self, agentId, query, universe, newState: dict, prev=False):
        """Find consumed data to pass to a State Manager."""
        # NOTE: queries are interpreted at runtime here
        match query["kind"]:
            case "Base":
                if prev:
                    return universe[agentId][query["content"]]
                agentState = newState.get(agentId)
                if agentState is None:
                    return None
                return agentState.get(query["content"])
            case "Prev":
                return self.find(agentId, query["content"], universe, newState, prev=True)
            case "Root":
                if prev:
                    return universe[agentId]
                return newState
            case "Agent":
                # agent always gets the previous state
                return universe[query["content"]]
            case "Access":
                base = self.find(agentId, query["content"]["base"], universe, newState, prev)
                if base is None:
                    return None
                return base.get(query["content"]["field"])
            case "Tuple":
                res = []
                for q in query["content"]:
                    found = self.find(agentId, q, universe, newState, prev)
                    if found is None:
                        return None
                    res.append(found)
                return res
            case _:
                return None

    def put(self, agentId, query, universe, newState: dict, data):
        """Put produced data into the universe."""
        match query["kind"]:
            case "Base":
                agentState = newState.get(agentId)
                if agentState is None:
                    agentState = {}
                    newState[agentId] = agentState
                agentState[query["content"]] = data
            case "Prev":
                raise Exception(f"Cannot produce prev query {query}")
            case "Root":
                pass
            case "Agent":
                res = universe[query["content"]]
                if res is None:
                    res = {}
                    universe[query["content"]] = res
                return res
            case "Access":
                baseQuery = query["content"]["base"]
                base = self.find(agentId, baseQuery, universe, newState)
                if base is None:
                    base = {}
                    self.put(agentId, baseQuery, universe, newState, base)
                base[query["content"]["field"]] = data
            case "Tuple":
                raise Exception(f"Tuple production not yet implemented")

    def simulate(self, iterations: int = 500):
        """Simulate the universe for a given number of iterations."""
        for _ in range(iterations):
            for agentId in self.init:
                t = self.times[agentId]
                universe = self.read(t - 0.001)
                if set(universe) == set(self.init):
                    newState = self.step(agentId, universe)
                    self.store[t, newState[agentId]["time"]] = newState
                    self.times[agentId] = newState[agentId]["time"]
