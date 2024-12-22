

def  scoreboard_ocr(img):
    """Gets the OCR value of the scoreboard and returns the values of the scoreboard in a list of lists. Each list contains
    the player IGN, kills, deaths, assists and which side they are on. This function will also ask for user input if the
    OCR fails to read the values."""
    start = 340

    scoreboard = []

    for i in range(10):

        img1 = img[start:start + 50, 330:700]
        res_name = reader.readtext(img1, detail=0, link_threshold=0)

        img1 = img[start:start + 50, 823:873]
        res_kills = reader.readtext(img1, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], mag_ratio=2.5,
                                    link_threshold=0, text_threshold=0, threshold=0, detail=0)

        img1 = img[start:start + 50, 880:930]
        res_deaths = reader.readtext(img1, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], mag_ratio=2.5,
                                     link_threshold=0, text_threshold=0, threshold=0, detail=0)

        img1 = img[start:start + 50, 930:980]
        res_assists = reader.readtext(img1, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], mag_ratio=2.5,
                                      link_threshold=0, text_threshold=0, threshold=0, detail=0)

        if not res_assists:
            res_assists = [input(f'Please confirm the assists for player {res_name}:')]
        elif not res_kills:
            res_kills = [input(f'Please confirm the kills for player {res_name}:')]
        elif not res_deaths:
            res_deaths = [input(f'Please confirm the deaths for player {res_name}:')]
        elif not res_name:
            res_deaths = [input(f'Please confirm the IGN for player number {i + 1} (according to scoreboard):')]

        b1, g1, r1 = img[start + 25, 278]

        if g1 < 100 and r1 > 200 and b1 < 100:
            side = 'opponent'

        else:
            side = 'team'

        scoreboard.append([res_name[0], res_kills[0], res_deaths[0], res_assists[0], side])

        start = start + 52

    return scoreboard