def correct_agent_name(agent_name):
    closest_match = get_close_matches(agent_name, list_of_agents, n=1)
    if closest_match:
        return closest_match[0]
    else:
        return 0