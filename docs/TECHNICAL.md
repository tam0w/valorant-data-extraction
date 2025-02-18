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

While this approach works for screenshots with a consistent format, it can be brittle. If the UI of the game changes, or if the screenshots are taken at a different resolution, these hard-coded coordinates may no longer be valid. An area for improvement could be to use more flexible methods for locating regions of interest, such as feature detection or relative positioning.

## Improvement Opportunities

While Practistics is a robust and functional system, there are several areas where it could potentially be improved:

1. **Dynamic Coordinates**: As mentioned, the reliance on hard-coded coordinates for image processing can be brittle. Investigating methods to dynamically locate regions of interest could make the system more resilient to changes in the game's UI or screenshot format.

2. **Redundant Functions**: Some parts of the codebase contain functions that perform similar tasks. For example, the `get_player_and_agents_names` function contains two nearly identical blocks of code for processing the top and bottom halves of the image. Refactoring these into a single, reusable function could improve code maintainability.

3. **Error Handling**: While the code does include some error handling, there are many potential edge cases that aren't currently handled, such as missing or corrupted screenshots. More comprehensive error handling could make the system more robust.

4. **Configuration Management**: Currently, many of the system's configurations (such as file paths and OCR settings) are hard-coded into the scripts. Moving these into a separate configuration file could make the system easier to manage and adapt to different environments.

5. **Performance Optimization**: Some of the image processing tasks, particularly those that involve scanning the entire image pixel by pixel, could potentially be optimized for better performance. Techniques like downsampling or using more efficient color space representations could be explored.

6. **Code Documentation**: While the code is commented, there is room for more extensive documentation, particularly around the expected format of the input screenshots and the structure of the output data.

For developers looking to contribute to Practistics, the best starting point is to familiarize yourself with the main modules and their interactions. From there, dive into the specific functions to understand how they process and transform the data. Keep in mind the overall data flow and the structure of the output data.

As with any complex system, don't hesitate to experiment, debug, and ask questions. The beauty of a modular, well-commented codebase is that it invites exploration and understanding.

Happy coding, and may your data always be insightful!
