import re

# Regex Patterns
RE_BECAME_INFECTED = re.compile(
    r"\[PSM\] Agent\s+(-?\d+)\s+became infected at (\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}).*"
)

def parse_log_file_for_infections(log_path):
    """
    Returns a set of agent IDs that 'became infected' in this run.
    """
    infected_agents = set()
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = RE_BECAME_INFECTED.search(line)
            if match:
                agent_id = int(match.group(1))
                infected_agents.add(agent_id)
    return infected_agents

def compute_infection_rates(log_files, universal_ids=None):
    """
    :param log_files: list of log file paths
    :param universal_ids: optional set of agent IDs if you want to track them all,
                          even if never infected => 0%
    :return: dict agent_id -> fraction of runs infected
    """
    all_infected_sets = []
    discovered_agents = set()

    for lf in log_files:
        inf_set = parse_log_file_for_infections(lf)
        all_infected_sets.append(inf_set)
        discovered_agents |= inf_set

    # If universal_ids is provided, we'll merge it so that those not discovered => 0 infections
    if universal_ids is not None:
        discovered_agents |= universal_ids

    n_runs = len(log_files)
    counter_infected = {a_id: 0 for a_id in discovered_agents}

    for inf_set in all_infected_sets:
        for a_id in inf_set:
            counter_infected[a_id] += 1

    infection_rate = {}
    for a_id in discovered_agents:
        infection_rate[a_id] = counter_infected[a_id] / n_runs

    return infection_rate


if __name__ == "__main__":
    logs = [f"log{i}.txt" for i in range(1, 61)]
    # If you want a known set: universal_ids = set(range(-1, 24))
    # else just let the script discover them.
    universal_agent_ids = {-1, 0, 3, 5, 8, 10, 14, 15, 17, 20, 23}
    rates = compute_infection_rates(logs, universal_ids=universal_agent_ids)

    print("Infection rates per agent across these runs:")
    for agent_id, val in sorted(rates.items()):
        print(f"Agent {agent_id}: {val:.2%}")
