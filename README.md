
# Practistics Scrim OCR

Practistics Scrim OCR is an open-source project designed to capture and process screenshots of VALORANT private scrim match scoreboards, summaries, and timelines. It uses OCR (Optical Character Recognition) to extract data from images and logs the information for further analysis.

Practistics Scrim OCR was intended for teams, to be used to extract tabular data match-by-match, allow technical and non-technical analysts to aggregrate and analyze performance in multiple practice matches. That is where the value would lie in using it. I wrote this OCR script since there wasn't really a way to access hidden scrim data post the scrim. The data output structure of this script is a .csv file. For that reason the code is written to generate CSV files (almost everything is a bunch of lists, far from ideal).

## Features

- Capture screenshots of game scoreboards, summaries, and timelines.
- Process and extract data from images using OCR.
- Log and save the captured data and images for analysis.

## Requirements

- Python 3.11 (recommended)
- pip (Python package installer)

## Installation

1. Clone the repository (or download the code):
    ```sh
    git clone https://github.com/yourusername/practistics.git
    cd practistics
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### 1. Running the Application

1. Navigate to the project directory:
    ```sh
    cd practistics
    ```

2. Run the main script:
    ```sh
    python main.py
    ```

### 2. Capturing Screenshots

- **Summary Screenshot**: Press `s` to capture the summary screenshot.
- **Scoreboard Screenshot**: Press `b` to capture the scoreboard screenshot.
- **Timeline Screenshot**: Press `p` to capture a timeline screenshot.
- **Finish Capturing**: Press `q` to finish capturing timeline screenshots.

You can also read images from a folder. They are saved in a folder whenever an error occurs mid process. To read images from a folder for testing purposes, use the `read_images_from_folder` function in `core/data_capture_module/capture.py`.

### 3. Analysis

Once the processing of the images is completed, an output .csv will be generated. This can be used to perform analysis on the game in applications like Tableau, PowerBI, or just R and Python. As of right now, the web dashboard to view analytics is not LIVE.

# Game Data Documentation

This dataset captures detailed round-by-round game information from competitive matches. Each row represents a single round, tracking everything from player actions and economy to spatial positioning and round outcomes. It's particularly useful for analyzing round dynamics, player performance, and strategic patterns.

## Sample Data Output

Here's a simplified view of the data (first 3 rows, selected columns):

| sides    | fk_player | fk_death | outcomes | bombsites | kills_team | kills_opp |
|----------|-----------|-----------|----------|-----------|------------|-----------|
| Defense  | Breach    | Yoru      | loss     | A         | 3          | 5         |
| Defense  | Clove     | Clove     | loss     | B         | 1          | 5         |
| Defense  | Chamber   | Neon      | loss     | A         | 0          | 5         |

## Available Data Points

The dataset includes 21 columns capturing various aspects of each round:

1. **Basic Round Info**
   - Side played on the map [sides]
   - Round outcome [outcomes]
   - Targeted bombsite [bombsites]
   - Round index, zero-based [Unnamed: 0]

2. **Player Actions**
   - Player who secured first kill [fk_player]
   - Player who died first [fk_death]
   - First blood player details [fbs_players]
   - Death-related player information [dt_players]
   - Timing of first kill in seconds [first_kill_times]

3. **Objective Actions**
   - Plant attempt indicator [plants]
   - Defuse attempt indicator [defuses]
   - First action was plant indicator [first_is_plant]

4. **Economy & Equipment**
   - Team's economic status [buy_info_team]
   - Opposition's economic status [buy_info_oppo]
   - AWP presence and usage info [awp_info]

5. **Round Statistics**
   - Team kill count [kills_team]
   - Opposition kill count [kills_opp]
   - Anchor position timing [anchor_times]
   - Team that got first blood [fb_team]
   - True first blood verification [true_fb]

6. **Event Timeline**
   - Detailed round event sequence [round_events]
     Format: [player, target, timestamp, team, action_type]

## Data Types and Formats

- Boolean fields: `plants`, `defuses`, `first_is_plant`, `true_fb`
- Integer fields: `kills_team`, `kills_opp`, `first_kill_times`, `anchor_times`
- String fields: `sides`, `fk_player`, `fk_death`, `outcomes`, `bombsites`
- Complex fields: `round_events` contains timestamped sequences of format:
  [player, target, timestamp, team, action_type]

The `round_events` field provides a comprehensive timeline of each round, capturing all significant actions with their corresponding timestamps and actors.                                                                                                                                                               |

# Application

This is one of the first pieces of software I wrote so its a bit weirdly written. We extract all the images of the post-game stats screens, do some image processing, some OCR, some text manipulation to get post-game data in a tabular format round by round. When extracting the data points, most of the extraction happens data point by data point rather for EACH round, rather than a more round by round approach (round 1 kills, round 2 kills, round 3 kills... round 1 deaths, round 2 deaths, round 3 deaths... are extracted, rather than round 1 kills, round 1 deaths, round 1 first blood, round 1 first death..)

We use `easyocr` as the OCR library.  

## Project Structure

```
practistics/
├── core/
│   ├── data_capture_module/
│   │   └── capture.py
│   ├── logger_module/
│   │   └── logger.py
│   ├── ocr_module/
│   │   └── ocr.py
│   └── processing_module/
│       └── text_helpers.py
│       └── img_helpers.py
├── requirements.txt
└── README.md
```

### Core Modules

- **data_capture_module**: Contains the script for capturing screenshots and reading images.
- **logger_module**: Contains the custom logger for logging messages and saving images.
- **ocr_module**: Contains the OCR setup for reading text from images.
- **processing_module**: Contains helper functions for processing text data and images.

## Contributing

Contributions are welcome, as soon as I can handle them. Please follow these steps to contribute to the main repo:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m "feat/fix/remove/update: Add your message here"
    ```
4. Push to the branch:
    ```sh
    git push origin feature/your-feature-name
    ```
5. Create a pull request.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.

## Note

This project is a work in progress that I do not have a lot of time to dedicate to. Its one of the first things I ever wrote, and all contributions and/or improvements are welcome.
For any questions or suggestions, please open an issue on GitHub. You can also reach out to me on my [twitter](https://twitter.com/tam0w), or on the project's [discord server](https://discord.gg/2eQ85rcQSQ).

---


