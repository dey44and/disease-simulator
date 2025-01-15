import re
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, date

import matplotlib.pyplot as plt

# -----------------------------------------------------------------
# REGEX PATTERNS (adjust if your logs differ)
# -----------------------------------------------------------------
RE_START_DAY = re.compile(r"A new simulation started at (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})")
RE_BECAME_INFECTED = re.compile(
    r"\[PSM\] Agent\s+(-?\d+)\s+became infected at (\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}).*"
)
RE_QUARANTINED = re.compile(r"\[PSM\] Agent\s+(-?\d+)\s+quarantined at end_of_day.*")
RE_RECOVERED = re.compile(r"\[PSM\] Agent\s+(-?\d+)\s+recovered after quarantine\.")

INFECTED_EVENT = "INFECTED"
QUARANTINED_EVENT = "QUARANTINED"
RECOVERED_EVENT = "RECOVERED"


# -----------------------------------------------------------------
# PARSE A SINGLE LOG
# -----------------------------------------------------------------
def parse_log_file(log_path):
    """
    Reads one log file, extracting events of interest:
      - INFECTED (with explicit date/time)
      - QUARANTINED (use 'current_day' from 'A new simulation started' lines)
      - RECOVERED (use 'current_day')
    Returns:
      events: list of (date_obj, agent_id, event_type)
      found_agents: set of all agent IDs that appear
    """
    events = []
    found_agents = set()
    current_day = None  # track day from "A new simulation started..."

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # 1) Check if day changed
            m_start = RE_START_DAY.search(line)
            if m_start:
                # "A new simulation started at 2025-01-20 07:30:00"
                day_str = m_start.group(1)  # e.g. "2025-01-20"
                day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                current_day = day_date
                continue

            # 2) Infect event
            m_inf = RE_BECAME_INFECTED.search(line)
            if m_inf:
                agent_id = int(m_inf.group(1))
                inf_day_str = m_inf.group(2)  # e.g. "2025-01-20"
                inf_day_date = datetime.strptime(inf_day_str, "%Y-%m-%d").date()
                events.append((inf_day_date, agent_id, INFECTED_EVENT))
                found_agents.add(agent_id)
                continue

            # 3) Quarantine
            m_quar = RE_QUARANTINED.search(line)
            if m_quar:
                agent_id = int(m_quar.group(1))
                found_agents.add(agent_id)
                if current_day:
                    events.append((current_day, agent_id, QUARANTINED_EVENT))
                continue

            # 4) Recovered
            m_rec = RE_RECOVERED.search(line)
            if m_rec:
                agent_id = int(m_rec.group(1))
                found_agents.add(agent_id)
                if current_day:
                    events.append((current_day, agent_id, RECOVERED_EVENT))
                continue

    return events, found_agents


# -----------------------------------------------------------------
# BUILD DAILY STATES
# -----------------------------------------------------------------
def build_daily_states(events, agent_ids):
    """
    :param events: list of (day_date, agent_id, event_type),
                   sorted or unsorted; we'll sort them here.
    :param agent_ids: set or list of agent IDs to track.
    :return: day->{"S":#, "I":#, "Q":#, "R":#}, for every day from earliest to latest.
    """
    # Sort events by (date, agent_id)
    events.sort(key=lambda x: (x[0], x[1]))

    # Find min_day and max_day
    if not events:
        return {}  # No events => everyone remains S? Up to you
    min_day = date.fromisoformat('2025-01-20')
    max_day = date.fromisoformat('2025-02-14')

    # Build a map: day => [ (agent_id, event_type), ... ]
    from collections import defaultdict
    daily_event_map = defaultdict(list)
    for (d, a_id, etype) in events:
        daily_event_map[d].append((a_id, etype))

    # Initialize current states
    current_state = {a_id: "S" for a_id in agent_ids}

    # We'll walk day by day from min_day to max_day
    day = min_day
    from collections import OrderedDict
    states_by_day = OrderedDict()

    while day <= max_day:
        # Apply any events for 'day'
        if day in daily_event_map:
            day_events = daily_event_map[day]
            for (a_id, etype) in day_events:
                if etype == "INFECTED":
                    current_state[a_id] = "I"
                elif etype == "QUARANTINED":
                    current_state[a_id] = "Q"
                elif etype == "RECOVERED":
                    current_state[a_id] = "R"

        # Now count S,I,Q,R
        s_count = sum(1 for a in agent_ids if current_state[a] == "S")
        i_count = sum(1 for a in agent_ids if current_state[a] == "I")
        q_count = sum(1 for a in agent_ids if current_state[a] == "Q")
        r_count = sum(1 for a in agent_ids if current_state[a] == "R")

        states_by_day[day] = {"S": s_count, "I": i_count, "Q": q_count, "R": r_count}

        # Move to next day
        day = day + timedelta(days=1)

    return states_by_day


# -----------------------------------------------------------------
# COMBINE MULTIPLE RUNS (AVERAGE)
# -----------------------------------------------------------------
def combine_daily_states(all_runs_states):
    """
    all_runs_states = list of dicts: day->{"S":#, "I":#, "Q":#, "R":#}
    We'll produce an average across runs for each day in the union of all days
    :return: Returns a dictionary will the values for S, I, Q, R for each day
    """
    all_days = set()
    for sbd in all_runs_states:
        all_days |= set(sbd.keys())
    all_days = sorted(all_days)

    combined = OrderedDict()

    for d in all_days:
        sum_s = 0
        sum_i = 0
        sum_q = 0
        sum_r = 0
        count_runs = 0
        for sbd in all_runs_states:
            if d in sbd:
                sum_s += sbd[d]["S"]
                sum_i += sbd[d]["I"]
                sum_q += sbd[d]["Q"]
                sum_r += sbd[d]["R"]
                count_runs += 1
        if count_runs > 0:
            combined[d] = {
                "S": sum_s / count_runs,
                "I": sum_i / count_runs,
                "Q": sum_q / count_runs,
                "R": sum_r / count_runs
            }
    return combined


# -----------------------------------------------------------------
# PLOT: S on TOP in STACKPLOT
# -----------------------------------------------------------------
def plot_siqr_combined(states_by_day, agent_ids, title="Combined SIQR"):
    """
    states_by_day: day->{"S":#, "I":#, "Q":#, "R":#} (possibly floats if averaged)
    agent_ids: the set/list of actual agent IDs
    We'll produce 2 plots:
      1) Stacked area with (R, Q, I, S) so S is on top
      2) Lines for S, I, Q, R
    """
    days_sorted = sorted(states_by_day.keys())
    s_vals, i_vals, q_vals, r_vals = [], [], [], []

    for d in days_sorted:
        day_dict = states_by_day[d]
        s_vals.append(day_dict["S"])
        i_vals.append(day_dict["I"])
        q_vals.append(day_dict["Q"])
        r_vals.append(day_dict["R"])

    # total population => the number of agent_ids
    total_pop = len(agent_ids)

    # Convert to fraction if you'd prefer a proportion
    s_frac = [v / total_pop for v in s_vals]
    i_frac = [v / total_pop for v in i_vals]
    q_frac = [v / total_pop for v in q_vals]
    r_frac = [v / total_pop for v in r_vals]

    x_vals = range(len(days_sorted))
    day_labels = [d.strftime("%Y-%m-%d") for d in days_sorted]

    # --- Stacked area with S on top => pass [r,q,i,s]
    plt.figure(figsize=(10, 6))
    plt.stackplot(
        x_vals,
        i_frac, q_frac, r_frac, s_frac,
        labels=["INFECTED", "QUARANTINED", "RECOVERED", "SUSCEPTIBLE"],
        colors=["salmon", "khaki", "lightgreen", "skyblue"]
    )
    plt.xticks(x_vals, day_labels, rotation=45)
    plt.xlabel("Days")
    plt.ylabel("Proportion of population")
    plt.title(f"{title} (Stacked area)")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.show()

    # --- Line chart (S, I, Q, R in "normal" order)
    plt.figure(figsize=(10, 6))
    # plt.plot(x_vals, s_frac, label="SUSCEPTIBLE", color="skyblue")
    plt.plot(x_vals, i_frac, label="INFECTED", color="salmon")
    plt.plot(x_vals, q_frac, label="QUARANTINED", color="khaki")
    plt.plot(x_vals, r_frac, label="RECOVERED", color="lightgreen")
    plt.xticks(x_vals, day_labels, rotation=45)
    plt.xlabel("Days")
    plt.ylabel("Proportion of population")
    plt.title(f"{title} (Line chart)")
    plt.legend()
    plt.tight_layout()
    plt.show()


# -----------------------------------------------------------------
# MAIN PROCESS: MULTIPLE LOGS => SINGLE PLOT
# -----------------------------------------------------------------
def process_multiple_logs_and_combine(log_files):
    """
    This function should:
        1) Parse each log => gather events & found_agents
        2) Build daily states for each run
        3) Combine => average
        4) Plot one stacked + one line chart
    """
    all_runs_states = []
    # TODO: Find a way to extract these IDs from a yaml (better than hardcoding the ids)
    universal_agent_ids = {-1, 0, 3, 5, 8, 10, 14, 15, 17, 20, 23}

    # Parse each log file
    for log_f in log_files:
        events, _ = parse_log_file(log_f)
        sbd = build_daily_states(events, universal_agent_ids)
        all_runs_states.append(sbd)

    # Combine daily states
    combined_sbd = combine_daily_states(all_runs_states)

    # Plot
    plot_siqr_combined(combined_sbd, universal_agent_ids, title="The evolution of SIQR model along the 28 days")


if __name__ == "__main__":
    logs = [f"log{i}.txt" for i in range(1, 61)]
    process_multiple_logs_and_combine(logs)
