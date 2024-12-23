def side_first_half():
    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    error_data['summary'] = cv_image
    file = cv_image[300:400, 1300:1500]
    gray = cv.cvtColor(file, cv.COLOR_RGB2BGR)
    res1 = reader.readtext(gray, detail=0)
    result = res1[0].__str__().lower()

    if result.__contains__('def'):
        first = "Defense"
        second = "Attack"
    else:
        second = "Defense"
        first = "Attack"
    sides = ([first] * 12 + [second] * 12)

    return sides


def total_events(tl_ss):
    """Total events including plants and defuses. Number of events per """

    events_team_counter_each_round = []
    events_opponent_counter_each_round = []
    list_of_sides_of_each_event_all_rounds = []

    for pic in tl_ss:

        start = 510
        counter_opp = 0
        counter_team = 0
        specific_round_events = []

        while True:
            b1, g1, r1 = pic[start, 940]
            if g1 > 190 and b1 > 100:
                counter_team += 1
                specific_round_events.append('team')
            if g1 < 100 and r1 > 200 and b1 < 100:
                counter_opp += 1
                specific_round_events.append('opponent')
            if b1 < 100 and g1 < 100 and r1 < 100:
                events_team_counter_each_round.append(counter_team)
                events_opponent_counter_each_round.append(counter_opp)
                list_of_sides_of_each_event_all_rounds.append(specific_round_events)
                break
            start += 38

    return events_team_counter_each_round, events_opponent_counter_each_round, list_of_sides_of_each_event_all_rounds

def bombsites_plants(tl_ss, map_name):
    spike_p = os.path.join(folder_path, "spike.png")
    spike = cv.imread(spike_p)

    sites = []

    for image in tl_ss:

        minimap = image[490:990, 1270:1770]
        resu = cv.matchTemplate(minimap, spike, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(resu)
        x, y = max_loc

        if max_val > 0.70:

            if map_name == 'bind':
                site = 'B' if x < 250 else 'A'

            elif map_name == 'ascent':
                site = 'B' if y < 250 else 'A'

            elif map_name == 'haven':
                if y < 150:
                    site = 'A'
                elif 150 < y < 280:
                    site = 'B'
                else:
                    site = 'C'

            elif map_name == 'lotus':
                if x < 150:
                    site = 'C'
                elif 150 < x < 300:
                    site = 'B'
                else:
                    site = 'A'

            elif map_name == 'pearl':
                if x < 250 and 90 < y < 210:
                    site = 'B'
                if x > 250 and 90 < y < 210:
                    site = 'A'

            elif map_name == 'fracture':
                if x > 250 and 190 < y < 290:
                    site = 'A'
                if x < 250 and 190 < y < 290:
                    site = 'B'

            elif map_name == 'split':
                site = 'B' if y > 250 else 'A'

            elif map_name == 'sunset':
                site = 'A' if x > 250 else 'B'

            elif map_name == 'breeze':
                site = 'A' if x > 250 else 'B'

            elif map_name == 'icebox':
                site = 'A' if y > 200 else 'B'

            else:
                site = 'unclear'

            sites.append(site)

        else:

            sites.append("False")

    return sites

def get_first_bloods(images):

    greens = []

    for image in images:
        b, g, r = image[520, 1150]
        greens.append(g)

    for green in greens:
        flag = 'team' if green > 100 else 'opponent'
        who_fb.append(flag)

    for i in range(len(events_team)):
        if plants[i] is True:

            if sides[i] == 'Attack':
                events_team[i] -= 1
            else:
                events_opp[i] -= 1

        if defuses[i] is True:
            if sides[i] == 'Defense':
                events_team[i] -= 1
            else:
                events_opp[i] -= 1
