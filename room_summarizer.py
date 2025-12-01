import csv
import json
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional
from urllib import error, request

ROOMS_FILE = Path("THM_Rooms_Sheet1.json")
TEAMS_FILE = Path("teams1_1.json")


def load_rooms() -> List[str]:
    data = json.loads(ROOMS_FILE.read_text())
    rooms = data.get("rooms", [])
    return [room for room in rooms if isinstance(room, str)]


def load_teams() -> List[Dict[str, Any]]:
    data = json.loads(TEAMS_FILE.read_text())
    teams = data.get("teams", [])
    return [team for team in teams if isinstance(team, dict)]


def summarize_room(room: str, teams: List[Dict[str, Any]]) -> Dict[str, Any]:
    relevance = {}
    for team in teams:
        role_name = team.get("role_en") or team.get("name_en") or team.get("id", "unknown")
        relevance[role_name] = {
            "score": None,
            "justification": "Cannot rate relevance because the room dataset only provides titles without descriptions."
        }
    return {
        "Room Title": room,
        "Overview": "No description provided in source data.",
        "Skills Covered": "Not provided in source data.",
        "Tools & Technologies": "Not provided in source data.",
        "Difficulty": "Unknown (not provided)",
        "Key Takeaways": "Insufficient information to extract takeaways.",
        "Hours": "Unknown",
        "Relevance by IT Role": relevance,
    }


def slugify_room_name(room: str) -> str:
    """Create a best-effort TryHackMe slug from the room title."""

    return room.strip().lower().replace(" ", "-")


def research_room(room: str, timeout: int = 10) -> Dict[str, Any]:
    """Attempt to fetch room details from the public TryHackMe API.

    The function is defensive and never raises network exceptions. If the
    endpoint cannot be reached or returns unexpected data, the result will note
    the failure reason so consumers can decide whether to retry manually.
    """

    slug = slugify_room_name(room)
    url = f"https://tryhackme.com/api/room/{slug}"
    try:
        with request.urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read())
    except error.URLError as exc:  # Includes HTTPError
        return {
            "room": room,
            "source": url,
            "status": "unreachable",
            "reason": str(exc),
        }
    except json.JSONDecodeError as exc:
        return {
            "room": room,
            "source": url,
            "status": "invalid-json",
            "reason": str(exc),
        }

    return {
        "room": room,
        "source": url,
        "status": "ok",
        "data": payload,
    }


def research_missing_data(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Collect research results for rooms lacking descriptions.

    Args:
        limit: Optional cap on the number of rooms to query to avoid excessive
            network calls during exploration.

    Returns:
        List of research result dictionaries with status indicators so callers
        can understand which rooms still need manual input.
    """

    rooms = load_rooms()
    if limit is not None:
        rooms = rooms[:limit]

    results: List[Dict[str, Any]] = []
    for room in rooms:
        results.append(research_room(room))
    return results


def start_research(batch_size: int = 50) -> Iterable[List[Dict[str, Any]]]:
    rooms = load_rooms()
    teams = load_teams()
    for start in range(0, len(rooms), batch_size):
        batch = rooms[start:start + batch_size]
        yield [summarize_room(room, teams) for room in batch]


def download_results(filename: str, fmt: str = "json", batch_size: int = 50) -> Path:
    fmt = fmt.lower()
    batches = list(start_research(batch_size=batch_size))
    flat_results = [entry for batch in batches for entry in batch]
    output_path = Path(filename)
    if fmt == "json":
        output_path.write_text(json.dumps(flat_results, indent=2))
    elif fmt == "csv":
        fieldnames = [
            "Room Title",
            "Overview",
            "Skills Covered",
            "Tools & Technologies",
            "Difficulty",
            "Key Takeaways",
            "Hours",
        ]
        with output_path.open("w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in flat_results:
                writer.writerow({field: entry.get(field, "") for field in fieldnames})
    else:
        raise ValueError("Unsupported format. Use 'json' or 'csv'.")
    return output_path


if __name__ == "__main__":
    # Example usage: generate JSON output for all rooms
    output = download_results("summaries.json", fmt="json")
    print(f"Saved {output}")
