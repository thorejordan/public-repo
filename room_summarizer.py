import json
import csv
from pathlib import Path
from typing import Iterable, List, Dict, Any

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
