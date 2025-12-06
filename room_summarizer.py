import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
ROOMS_PATH = ROOT / "THM_Rooms_Sheet1.json"
MODULES_PATH = ROOT / "structured_tryhackme_modules.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summarize_rooms():
    data = load_json(ROOMS_PATH)
    rooms = data.get("rooms", []) if isinstance(data, dict) else []

    total_rooms = len(rooms)
    uniques = set(rooms)
    duplicate_counts = Counter(room for room in rooms if room not in uniques or rooms.count(room) > 1)
    # Counter above over-counts; recompute properly for values >1
    duplicate_counts = Counter({room: count for room, count in Counter(rooms).items() if count > 1})

    print("Rooms dataset summary")
    print(f"- Total entries: {total_rooms}")
    print(f"- Unique rooms: {len(uniques)}")
    if duplicate_counts:
        top_duplicates = duplicate_counts.most_common(5)
        printable = ", ".join(f"{room} (x{count})" for room, count in top_duplicates)
        print(f"- Top duplicates (showing up to 5): {printable}")
    else:
        print("- No duplicates detected")


def summarize_modules():
    modules = load_json(MODULES_PATH)
    if not isinstance(modules, list):
        print("Modules dataset is not a list; cannot summarize")
        return

    difficulty_counts = Counter()
    domain_counts = Counter()

    for module in modules:
        difficulty = module.get("anspruchsniveau", "Unbekannt")
        difficulty_counts[difficulty] += 1
        for domain in module.get("fachgebiet_zuordnung", []) or []:
            domain_counts[domain] += 1

    print("\nStructured modules summary")
    print(f"- Total modules: {len(modules)}")
    print("- Modules by difficulty:")
    for level, count in difficulty_counts.most_common():
        print(f"  - {level}: {count}")

    print("- Top 5 domains:")
    for domain, count in domain_counts.most_common(5):
        print(f"  - {domain}: {count}")


def main():
    summarize_rooms()
    summarize_modules()


if __name__ == "__main__":
    main()
