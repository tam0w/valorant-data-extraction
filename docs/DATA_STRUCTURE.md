
# The Round-by-Round Structure

The Practistics data is structured in a way that reflects the natural flow of a VALORANT match. Each row in the dataset represents a single round. You can think of each round as a chapter in the story of the match.
This round-by-round format allows for analysis at varying levels of detail. You can aggregate the data to understand overall match trends, or drill down into specific rounds to examine pivotal moments.

## A Sample of the Data

To make this more concrete, let's look at a sample of the actual data:

| sides   | plants | defuses | fk_player | ... | fbs_players  | dt_players       | first_kill_times | bombsites | ... |
|---------|--------|---------|-----------|-----|--------------|------------------|------------------|-----------|-----|
| Defense | True   | False   | Breach    | ... | SVGUnknown   | DaddyChill       | 7                | A         | ... |
| Defense | True   | False   | Clove     | ... | SNELID       | Gunda Ganesh     | 23               | B         | ... |
| Defense | True   | False   | Chamber   | ... | krishna      | Togepi           | 4                | A         | ... |
| Defense | True   | False   | Yoru      | ... | DaddyChill   | Tatsumi          | 10               | B         | ... |

The `...` indicate columns that have been omitted for readability. But even in this condensed view, we can start to see the story of each round taking shape. We can see which side your team was on, whether the spike was planted, who got the first elimination and when, and so on.


## Data Fields

Here's a detailed breakdown of each field in the dataset:

### 1. `Unnamed: 0`: Round Counter
- Data Type: Integer 
- Description: A counter uniquely identifying each round, starting from 0.

### 2. `sides`: Team Side
- Data Type: String
- Description: The side your team played in the round.
- Possible Values: `"Attack"`, `"Defense"`

### 3. `plants`: Spike Planted
- Data Type: Boolean
- Description: Whether your team planted the spike.
- Possible Values: `True`, `False`

### 4. `defuses`: Spike Defused  
- Data Type: Boolean
- Description: Whether your team defused the spike.
- Possible Values: `True`, `False`

### 5. `fk_player`: First Blood Attacker
- Data Type: String 
- Description: The player who got the first elimination.
- Possible Values: Player name, or `""` if no eliminations.

### 6. `fk_death`: First Blood Victim
- Data Type: String
- Description: The player eliminated in the first blood.
- Possible Values: Player name, or `""` if no eliminations.

### 7. `outcomes`: Round Outcome
- Data Type: String 
- Description: Whether your team won or lost the round.
- Possible Values: `"win"`, `"loss"`

### 8. `fb_team`: First Blood Team
- Data Type: String
- Description: Which team got the first elimination.
- Possible Values: `"team"` (your team), `"opponent"`, `"none"` 

### 9. `awp_info`: AWP Purchases
- Data Type: String
- Description: Which teams bought AWPs.
- Possible Values: `"team"`, `"opponent"`, `"both"`, `"none"`

### 10. `buy_info_team`: Team Average Loadout Value 
- Data Type: Integer
- Description: The average credits spent by your team.

### 11. `buy_info_oppo`: Opponent Average Loadout Value
- Data Type: Integer 
- Description: The average credits spent by the opponent team.

### 12. `kills_team`: Team Eliminations
- Data Type: Integer
- Description: The number of eliminations by your team.

### 13. `kills_opp`: Opponent Eliminations
- Data Type: Integer
- Description: The number of eliminations by the opponent team.

### 14. `first_is_plant`: First Action was Plant
- Data Type: Boolean
- Description: Whether the first major action was a spike plant by your team.
- Possible Values: `True`, `False`

### 15. `fbs_players`: First Blood Player
- Data Type: String
- Description: The player who got the first elimination.
- Possible Values: Player name, or `""` if no eliminations.

### 16. `dt_players`: All Elimination Players 
- Data Type: String
- Description: All players with eliminations, in the format `"PlayerA PlayerB ..."`.

### 17. `first_kill_times`: First Blood Timestamp
- Data Type: Float 
- Description: The time in seconds of the first elimination.
- Possible Values: Non-negative float, or `-1` if no eliminations.

### 18. `bombsites`: Plant Site
- Data Type: String
- Description: The site where the spike was planted.
- Possible Values: `"A"`, `"B"`, `"C"`, or `""` if no plant.

### 19. `true_fb`: Decisive First Blood
- Data Type: Boolean
- Description: Whether the first elimination was decisive to the round outcome.
- Possible Values: `True`, `False`

### 20. `anchor_times`: Defender Rotation Time
- Data Type: Float
- Description: The time in seconds when defenders rotated off their initial positions.
- Possible Values: Non-negative float if defending, `0` if attacking.

### 21. `round_events`: Round Event Timeline  
- Data Type: String
- Description: A JSON list of major events, each in the format `[Player, Victim, Timestamp, Team, EventType]`.
  - `Player` and `Victim` are player names (`""` for non-eliminations).
  - `Timestamp` is the event time in seconds from round start.  
  - `Team` is `"team"` (your team) or `"opponent"`.
  - `EventType` is `"Kill"`, `"Plant"`, or `"Defuse"`.

## Technical Notes

With this dataset, you can perform analyses such as:

1. Calculating first blood win rates by player and team
2. Evaluating economy management and its impact on round outcomes  
3. Assessing site control and retake success rates
4. Examining player performance metrics like K/D, KAST, clutches
5. Visualizing common opponent strategies and setups

The structured format allows for a wide range of analytical approaches. The key is to formulate the right questions and leverage the appropriate data fields to answer them.

When working with this data, keep in mind:

- Parse data types correctly (e.g. integers, booleans, JSON)
- Handle missing values appropriately
- Aggregate data as needed for your analysis (e.g. by player, team, map)
- Choose visualizations that effectively communicate your insights

Remember, the goal is to translate this data into actionable information to improve your team's gameplay. Always consider the practical applications as you explore the data.
