# Technical Documentation

## System Architecture

Practistics is a data extraction tool for VALORANT that processes match screenshots to generate structured data for analysis. The system transforms visual data into CSV/JSON files through OCR and image processing.

The codebase is organized as a `core` package with specialized modules:

- **capture** → Image acquisition (screenshots or disk loading)
- **ocr** → Text extraction via EasyOCR with optional GPU acceleration
- **image_processing** → Computer vision operations (template matching, color detection)
- **data_processing** → Game logic and data normalization
- **api** → Fetches valid agent/map names from VALORANT API for validation
- **export** → Data serialization to CSV/JSON
- **logger** → Logging with context tracking
- **config** → Configuration management
- **types** → Type definitions

The lower-level modules handle generic operations (text extraction, template matching) while `data_processing` contains all the VALORANT-specific logic for interpreting what that extracted data means in the context of the game.

## Core Design Decisions

### Resolution and Coordinate Dependency

**Important limitation**: The tool only works at 1920x1080 native resolution. All coordinates are hard-coded for this specific resolution, and using any other resolution will cause data extraction to fail.

The system relies heavily on pixel coordinates to locate UI elements. Player names appear at specific positions, round events show up at known locations, and the minimap has fixed bounds. While this makes the tool brittle to UI changes, it's a practical approach given that VALORANT's UI is consistent at a given resolution.

To handle cases where exact coordinates aren't reliable, the system uses a semi-dynamic approach in some areas. Instead of reading directly at position (495, 200), it might:
- Start at y=495 and scan downward until it finds a green pixel (indicating team color)
- Then extract the player name from that dynamically found position
- Continue scanning with safety limits to prevent infinite loops

This hybrid approach balances the simplicity of coordinate-based extraction with some flexibility for minor UI variations.

### Context Tracking in Logger

The logging system maintains a context stack that gets included with log messages. When processing round 5 and extracting a kill event, the log output includes this context:

```
[operation=process_match | round=5 | event_type=kill] Extracted kill event: Jett → Sage at 23s
```

The implementation uses a dictionary to store context and a push/clear pattern:
- `push_context()` adds key-value pairs to the current context
- `clear_context()` removes the context
- All log messages automatically include the active context

This helps with debugging by showing exactly what the system was processing when an issue occurred.

### Data Normalization Approach

OCR is inherently imperfect. The system handles OCR errors through fuzzy matching to find the closest valid agent or map name. When confidence is low, it falls back to manual input:

- Agent names use a 0.6 similarity threshold
- Special cases like "KAY/O" (often read as "KAYO") have explicit handlers
- Unrecognized names prompt the user for confirmation

This approach acknowledges that OCR won't be perfect and builds in ways to handle that imperfection rather than producing incorrect data.

## Key Architectural Patterns

### The Singleton Logger

The logging system uses a singleton pattern to maintain context state across the entire application:

```python
class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
```

This ensures context added in one module is available in all subsequent log messages without passing state between functions.

### Three-Layer Fallback Strategy

External operations have multiple fallback layers:

1. **Primary source** (VALORANT API call for valid agents/maps)
2. **Cache** (Recently fetched data saved locally)
3. **Hardcoded defaults or manual input** (Built-in agent list or user prompt)

The tool's goal is to make data collection easier, not fully automate it. Since Riot doesn't provide match history APIs for custom games and OCR isn't 100% accurate, there are times when the system asks for user confirmation rather than guessing. This semi-automated approach ensures accuracy while still saving significant manual work.

### Type Safety with TypedDict

The codebase uses `TypedDict` for data structures:

```python
class RoundData(TypedDict):
    round_number: int
    events: List[EventData]
    outcome: str
    side: str
```

This provides type hints while keeping the data as dictionaries, making JSON serialization straightforward without custom encoders.

## Data Flow

### Processing Pipeline

Data moves through several stages:

**RAW** → **EXTRACTED** → **NORMALIZED** → **VALIDATED** → **EXPORTED**

- **Raw**: Screenshots as numpy arrays
- **Extracted**: Raw OCR text and template matching results
- **Normalized**: Corrected names, parsed timestamps
- **Validated**: Consistency checks applied
- **Exported**: CSV/JSON files

The pipeline has some separation between stages, though there's coupling in places where round processing needs to access multiple types of data simultaneously.

### Event Resolution Strategy

When both teams have the same agent (e.g., both have Jett), the system needs to determine which player performed an action. It uses:

- **Color detection** to identify team (green for allies, red for enemies)
- **Position mapping** (slots 0-4 are team, 5-9 are opponents)
- **Side information** passed through the event data

This multi-factor approach helps correctly attribute events even with duplicate agents on both teams.

## Performance Considerations

### GPU Acceleration

The system supports GPU acceleration for OCR through CUDA, providing significant speedup when available. If CUDA isn't available, it falls back to CPU processing. This is detected at startup:

```python
if torch.cuda.is_available():
    logger.debug("GPU acceleration enabled for OCR")
```

The acceleration is handled internally by EasyOCR, transparent to the rest of the system.

### API Caching

The caching system for VALORANT API data uses TTL-based invalidation:
- Agent lists: cached for 7 days
- Map lists: cached for 14 days

The cache helps reduce API calls and provides continuity when the API is unavailable. Even expired caches can be used with a warning if fresh data can't be fetched.

## Error Handling

When errors occur, the system:

1. Logs the full error with context
2. Generates a unique error ID for reference
3. Saves screenshots and logs to disk
4. Shows the user a simple message with the error ID
5. Continues processing if possible

This gives users something concrete to report while preserving debugging information for developers.

## Development Modes

The system supports several execution modes:

- **Normal mode**: Standard user output
- **Dev mode** (`--dev`): Verbose logging
- **Offline mode** (`--offline`): Skip API calls, use hardcoded data
- **Read mode** (`--read FOLDER`): Process pre-captured screenshots

Read mode is particularly useful for development, allowing you to test changes without recapturing screenshots each time.

## Limitations and Trade-offs

### Resolution Dependency
The tool only works at 1920x1080 resolution. Supporting multiple resolutions would require coordinate scaling or dynamic UI element detection, significantly increasing complexity.

### OCR Accuracy
OCR is never 100% accurate, especially with stylized game fonts. The system handles this through normalization and manual confirmation prompts when confidence is low.

### UI Changes
Game updates that change the UI layout will break the tool until coordinates are updated. This is an inherent limitation of screenshot-based extraction.

### Manual Intervention
The tool is semi-automated by design. Full automation isn't possible without official API support, so user confirmation is sometimes required to ensure data accuracy.
