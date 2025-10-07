"""Event definitions and utilities for swim records."""

# Age groups (USA Swimming standard)
AGE_GROUPS = ["10U", "11-12", "13-14", "15-16", "17-18", "Open"]

# SCY Events (Short Course Yards)
SCY_EVENTS = [
    "50-free",
    "100-free",
    "200-free",
    "500-free",
    "1000-free",
    "1650-free",
    "50-back",
    "100-back",
    "200-back",
    "50-breast",
    "100-breast",
    "200-breast",
    "50-fly",
    "100-fly",
    "200-fly",
    "100-im",
    "200-im",
    "400-im",
]

# LCM Events (Long Course Meters)
LCM_EVENTS = [
    "50-free",
    "100-free",
    "200-free",
    "400-free",
    "800-free",
    "1500-free",
    "50-back",
    "100-back",
    "200-back",
    "50-breast",
    "100-breast",
    "200-breast",
    "50-fly",
    "100-fly",
    "200-fly",
    "200-im",
    "400-im",
]

# SCM Events (Short Course Meters) - Same as LCM
SCM_EVENTS = LCM_EVENTS.copy()

# Event name formatting
STROKE_NAMES = {
    "free": "Freestyle",
    "back": "Backstroke",
    "breast": "Breaststroke",
    "fly": "Butterfly",
    "im": "Individual Medley",
}


def format_event_name(event_code: str) -> str:
    """Convert event code to display name.

    Args:
        event_code: Event code like "50-free" or "200-im"

    Returns:
        Display name like "50 Freestyle" or "200 Individual Medley"
    """
    parts = event_code.split("-")
    if len(parts) != 2:
        return event_code

    distance, stroke = parts
    stroke_name = STROKE_NAMES.get(stroke.lower(), stroke.title())

    return f"{distance} {stroke_name}"


def parse_api_event(event_str: str) -> tuple[str | None, str | None, str | None]:
    """Parse event string from API.

    Args:
        event_str: Event from API like "50 FR SCY" or "100 BACK LCM"

    Returns:
        Tuple of (distance, stroke, course) or (None, None, None) if parsing fails
    """
    if not event_str or not isinstance(event_str, str):
        return None, None, None

    parts = event_str.strip().split()
    if len(parts) < 3:
        return None, None, None

    distance = parts[0]
    stroke_code = parts[1].upper()
    course = parts[2].upper()

    # Map stroke codes to our format
    stroke_map = {
        "FR": "free",
        "BK": "back",
        "BACK": "back",
        "BR": "breast",
        "BREAST": "breast",
        "FL": "fly",
        "FLY": "fly",
        "IM": "im",
    }

    stroke = stroke_map.get(stroke_code)
    if not stroke:
        return None, None, None

    return distance, stroke, course.lower()


def create_event_code(distance: str, stroke: str) -> str:
    """Create event code from distance and stroke.

    Args:
        distance: Distance like "50", "100", "200"
        stroke: Stroke like "free", "back", "breast", "fly", "im"

    Returns:
        Event code like "50-free" or "200-im"
    """
    return f"{distance}-{stroke}"


def convert_time_to_seconds(time_str: str) -> float:
    """Convert swim time string to seconds for sorting.

    Args:
        time_str: Time like "21.45" or "1:42.15"

    Returns:
        Time in seconds as float, or inf if invalid
    """
    try:
        if not time_str or time_str == "":
            return float("inf")

        time_str = str(time_str).strip()

        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                mins, secs = parts
                return float(mins) * 60 + float(secs)
            elif len(parts) == 3:
                hours, mins, secs = parts
                return float(hours) * 3600 + float(mins) * 60 + float(secs)

        return float(time_str)
    except (ValueError, AttributeError):
        return float("inf")


def determine_age_group(age: int | float | str) -> str:
    """Determine age group from age.

    Args:
        age: Age as int, float, or string

    Returns:
        Age group like "10U", "11-12", "13-14", etc.
    """
    try:
        age_int = int(float(age))
    except (ValueError, TypeError):
        return "Open"

    if age_int <= 10:
        return "10U"
    elif age_int <= 12:
        return "11-12"
    elif age_int <= 14:
        return "13-14"
    elif age_int <= 16:
        return "15-16"
    elif age_int <= 18:
        return "17-18"
    else:
        return "Open"
