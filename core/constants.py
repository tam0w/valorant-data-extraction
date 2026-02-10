from core.types import ImageRegion

list_of_agents = [
    "Phoenix", "Raze", "Jett", "Yoru", "Neon", "Reyna", "Iso",
    "Sova", "Skye", "KAY/O", "Fade", "Breach", "Harbor", "Gekko",
    "Cypher", "Killjoy", "Chamber", "Sage", "Brimstone",
    "Omen", "Viper", "Astra", "Deadlock", "Clove"
]

list_of_maps = [
    "Ascent", "Bind", "Haven", "Split", "Icebox",
    "Breeze", "Fracture", "Pearl", "Lotus", "Sunset"
]

# All regions are ImageRegion(y_start, y_end, x_start, x_end) for 1920x1080

# Summary screen
SUMMARY_SIDES_REGION = ImageRegion(300, 400, 1300, 1500)
SUMMARY_SCORE_REGION = ImageRegion(70, 170, 700, 1150)
SUMMARY_MAP_REGION = ImageRegion(125, 145, 120, 210)

# Timeline screen (static regions)
TIMELINE_OUTCOME_REGION = ImageRegion(430, 470, 130, 700)
TIMELINE_ECONOMY_REGION = ImageRegion(425, 480, 1020, 1145)
TIMELINE_AWP_REGION = ImageRegion(450, 950, 650, 785)
TIMELINE_MINIMAP_REGION = ImageRegion(490, 990, 1270, 1770)

# Timeline event scanning
EVENT_START_Y = 500
EVENT_CHECK_X = 940
EVENT_KILL_X = 945
EVENT_DEATH_X = 1231
EVENT_ROW_HEIGHT = 36
EVENT_TIMESTAMP_X = (980, 1040)
EVENT_TYPE_X = (1150, 1230)
EVENT_KILLER_ICON_X_OFFSET = 0
EVENT_VICTIM_ICON_X_OFFSET = 0
EVENT_ICON_SIZE = 36
FIRST_BLOOD_CHECK_Y = 520
FIRST_BLOOD_CHECK_X = 1150

# Player extraction (from first timeline)
PLAYER_TEAM_START_Y = 495
PLAYER_OPPONENT_START_Y = 726
PLAYER_CHECK_X = 200
PLAYER_NAME_OFFSET = 3
PLAYER_REGION_WIDTH = 183
PLAYER_ROW_HEIGHT = 40
PLAYER_ROW_SPACING = 42

# BGR channel thresholds for detecting team-colored player rows
PLAYER_TEAM_GREEN_THRESHOLD = 90
PLAYER_OPPONENT_RED_THRESHOLD = 40

# Agent sprite extraction (from scoreboard)
SPRITE_TEAM_START_Y = 503
SPRITE_OPPONENT_START_Y = 724
SPRITE_CHECK_X = 161
SPRITE_ICON_OFFSET = 3
SPRITE_ICON_SIZE = 40
SPRITE_ROW_SPACING = 42

# BGR channel thresholds for detecting team-colored sprite rows
SPRITE_TEAM_GREEN_THRESHOLD = 100
SPRITE_OPPONENT_RED_THRESHOLD = 80
