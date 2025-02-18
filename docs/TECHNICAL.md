# System Overview

At its core, Practistics is a Python application that processes VALORANT match screenshots to extract rich game data. This data is then transformed and outputted in a structured format for further analysis.

The system comprises several modules, each responsible for a specific aspect of the data extraction pipeline:

1. **Data Capture Module**: Responsible for reading match screenshots, either from a specified directory or by capturing them in real-time.

2. **OCR Module**: Handles optical character recognition (OCR) to extract textual information from the screenshots.

3. **Image Processing Module**: Performs image processing tasks such as template matching, color detection, and cropping to extract specific visual elements.

4. **Text Processing Module**: Processes and formats the extracted textual data, preparing it for output.

5. **Main Module**: Orchestrates the entire data extraction process, coordinating the interaction between the different modules.

## Key Functionalities

Let's dive deeper into some of the key functionalities of Practistics.

### Data Capture

The data capture module, defined in `data_capture_module/capture.py`, is responsible for acquiring the match screenshots for processing. It provides two main functions:

1. `read_images_from_folder(sub_dir)`: Reads images from a specified subdirectory.
2. `screenshot_pages()`: Captures screenshots in real-time.

The choice between these two functions is left to the user, providing flexibility in how data is acquired.

### OCR with EasyOCR

Practistics heavily utilizes OCR to extract textual information from the screenshots. It uses the EasyOCR library, which is initialized in the `ocr_module/ocr.py` file:

```python
from core.ocr_module.ocr import reader
```

EasyOCR is a powerful Python library for OCR that works out of the box and supports multiple languages. In Practistics, it's used to read text from various sections of the screenshots, such as player names, scores, and buy information.

A typical usage of EasyOCR in the codebase looks like this:

```python
res = reader.readtext(cur_img, detail=0, width_ths=25)
```

Here, `reader` is the EasyOCR instance, `readtext` is the main OCR function, and `cur_img` is the image to be processed. The `detail` and `width_ths` parameters control the level of detail in the output and the width threshold for text detection, respectively.

### Image Processing

Practistics performs various image processing tasks to extract specific visual elements from the screenshots. These tasks are primarily handled by the functions in the `processing_module/image_helpers.py` file.

One common technique used is template matching, which is used to find the location of a specific image (the template) within a larger image. Here's an example from the `bombsites_plants` function:

```python
resu = cv.matchTemplate(minimap, spike, cv.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(resu)
```

In this snippet, `cv.matchTemplate` is used to find the location of the spike (bomb) icon within the minimap image. The `cv.TM_CCOEFF_NORMED` parameter specifies the matching method, which returns a "similarity score" between 0 and 1. The location with the highest score (`max_loc`) is considered the match location.

Another common technique is color detection, which is used to identify specific elements based on their color. Here's an example from the `total_events` function:

```python
b, g, r = pic[u, gr_check]
while g < 100 and r < 100 and b < 100:
    u += 1
    b, g, r = pic[u, gr_check]

if g < 100:
    counter_opp += 1
    specific_round_events.append('opponent')
else:
    counter_team += 1
    specific_round_events.append('team')
```

In this snippet, the function is scanning down a specific column of pixels (`gr_check`). It's looking for pixels where the green (`g`) and red (`r`) values are above 100. If `g` is below 100, it's considered an opponent event; otherwise, it's a team event. This color-based distinction is used to count the number of events for each team in each round.

### Data Structures

One key aspect to understand about the Practistics data is that most of it is structured as arrays, with one data point for each round. For instance, consider the return values of the `total_events` function:

```python
return events_team_counter_each_round, events_opponent_counter_each_round, list_of_sides_of_each_event_all_rounds
```

Here, `events_team_counter_each_round` and `events_opponent_counter_each_round` are lists where each element represents the number of events for the team and opponent, respectively, in a specific round. Similarly, `list_of_sides_of_each_event_all_rounds` is a list of lists, where each inner list represents the sides (team or opponent) of each event in a specific round.

This structure, where each list represents a specific attribute across all rounds, is common throughout the codebase. When working with this data, it's crucial to keep in mind that the index of each list corresponds to a specific round.

The current implementation heavily relies on parallel lists for related data. For example, in the `get_first_three_rounds_kill_data` function:

```python
def get_first_three_rounds_kill_data(first_event_is_plant_boolean_all_rounds,
                                   first_event_left_player,
                                   first_event_right_player,
                                   # ... more parallel lists
                                   ):
    fk_player = []
    fk_death = []
    sk_player = []
    sk_death = []
    tk_player = []
    tk_death = []
    # ... processing these parallel lists
```



### Hard-coded Coordinates

A significant portion of the image processing in Practistics relies on hard-coded pixel coordinates. These coordinates are used to crop specific regions of interest from the screenshots.

For example, in the `get_player_and_agents_names` function:

```python
st_u = 495
gr_check = 200
for i in range(5):
    b, g, r = image[st_u, gr_check]
    u = st_u
    while g < 90:
        u = u + 1
        b, g, r = image[u, gr_check]
    st_l = gr_check + 3
    _, new_g, _ = image[u, st_l]
    cur_img = image[u:u + 40, st_l:st_l + 180]
    st_u = u + 42
```

Here, `st_u`, `gr_check`, and `st_l` are hard-coded coordinates that are used to locate and crop the region containing the player and agent names. The function relies on the assumption that these names will always appear at these specific locations in the screenshot.

While this approach works for screenshots with a consistent format, it can be brittle. If the UI of the game changes, or if the screenshots are taken at a different resolution, these hard-coded coordinates are no longer be valid. An area for improvement could be to use more flexible methods for locating regions of interest, such as feature detection or relative positioning.

## Possible Improvements

### Dynamic Coordinate Management

The current implementation relies heavily on hard-coded coordinates for image processing, making it brittle in the face of UI changes. These hard-coded values appear throughout the codebase:

```python
# In total_events():
b, g, r = image[520, 1150]  # Team detection coordinates

# In get_player_and_agents_names():
st_u = 495  # Starting y-coordinate
gr_check = 200  # x-coordinate for color checking

# In scoreboard_ocr():
img1 = img[start:start + 50, 330:700]  # Player name region
```

We can make this more resilient by implementing a coordinate management system:

```python
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class UIRegion:
    name: str
    coordinates: Tuple[int, int, int, int]
    purpose: str

class CoordinateManager:
    def __init__(self):
        self.regions: Dict[str, UIRegion] = self._load_regions()
    
    def get_region(self, region_name: str) -> UIRegion:
        if region_name not in self.regions:
            raise ValidationError(f"Unknown region: {region_name}")
        return self.regions[region_name]
```

### Structured Data Types and Processing

The current implementation often uses parallel lists and multiple return values. This pattern appears in several functions:

```python
# Current approach in generate_all_round_info():
def generate_all_round_info(round_engagements_agents, 
                          list_of_sides_of_each_event_each_round,
                          plants_or_not, timestamps):
    rounds_engagements_events_data = round_engagements_agents
    # ... manipulating multiple lists
```

We can improve this with proper data structures:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RoundEvent:
    timestamp: int
    agent: str
    target: Optional[str]
    event_type: str
    side: str

@dataclass
class Round:
    events: List[RoundEvent]
    plants: bool
    side: str
```

### Error Handling and Validation

The current codebase uses basic error handling with silent failures or user prompts. This pattern appears in multiple places:

```python
# In get_player_and_agents_names():
if not res_assists:
    res_assists = [input(f'Please confirm the assists for player {res_name}:')]

# In correct_agent_name():
if closest_match:
    return closest_match[0]
else:
    return 0
```

We can implement comprehensive error handling:

```python
class ValidationError(Exception):
    pass

class OCRError(Exception):
    pass

def validate_agent_name(agent_name: str) -> str:
    match = get_close_matches(agent_name, self.static_data.agents, n=1)
    if not match:
        raise ValidationError(f"No match found for agent: {agent_name}")
    return match[0]
```

### Static Data Management

Currently, the code uses hard-coded lists and constants:

```python
from core.constants import list_of_agents

def correct_agent_name(agent_name):
    closest_match = get_close_matches(agent_name, list_of_agents, n=1)
    return closest_match[0] if closest_match else 0
```

We can improve this with a proper static data management system:

```python
class GameData:
    def __init__(self):
        self.agents = self._load_agent_data()
        self.maps = self._load_map_data()
    
    def _load_agent_data(self):
        """Load agent data from configuration files"""
        with open('config/agents.json', 'r') as f:
            return json.load(f)
    
    def validate_agent(self, name: str) -> Optional[str]:
        return process.extractOne(
            name,
            self.agents.keys(),
            score_cutoff=80
        )[0]
```

### Time Processing and Standardization

The codebase handles time processing in multiple places with string manipulation:

```python
def fix_times(timestamps):
    """Converts various timestamp formats to integers"""
    new_timestamps = []
    for round in timestamps:
        new_round = []
        for timestamp in round:
            if timestamp.startswith('0'):
                timestamp = int(timestamp.replace('0:0', '')
                              .replace('0:', '')
                              .replace('.', '')
                              .replace(':', ''))
```

We can standardize this with a proper time processing system:

```python
@dataclass
class GameTime:
    raw_time: str
    seconds: int
    
    @classmethod
    def parse(cls, timestamp: str) -> 'GameTime':
        try:
            if timestamp.startswith('0'):
                seconds = cls._parse_short_time(timestamp)
            else:
                seconds = cls._parse_long_time(timestamp)
            return cls(raw_time=timestamp, seconds=seconds)
        except ValueError as e:
            raise ValidationError(f"Invalid timestamp: {timestamp}")
```

### Code Organization

Many functions handle multiple responsibilities and process data linearly. This appears in functions like `total_events()`, `bombsites_plants()`, and `match_agent()`. We can improve this with a proper processing pipeline:

```python
class RoundProcessor:
    def __init__(self, static_data: GameData):
        self.static_data = static_data
    
    def process_round(self, image: np.ndarray) -> Round:
        """Process all aspects of a round in one pass"""
        events = self._extract_events(image)
        economy = self._process_economy(image)
        plants = self._process_plants(image)
        
        return Round(
            events=events,
            economy=economy,
            plants=plants,
            side=self._detect_side(image)
        )
```

These improvements work together to create a more maintainable and robust system. Each enhancement addresses patterns that appear throughout the codebase, making it easier for contributors to implement systematic improvements while maintaining the core functionality of extracting match data.

The improvements focus on:
- Creating clear data structures
- Implementing consistent error handling
- Centralizing configuration
- Standardizing data processing
- Improving code organization

For developers looking to contribute, these patterns provide a roadmap for systematic improvements while maintaining the tool's core functionality.
