import json
from pathlib import Path

from yaml import safe_load

def read_entry_key(key: str) -> tuple[int, str]:
    split_key = key.split()
    return int(split_key[0]), split_key[1]

class Ruleset:
    def __init__(self, path: Path):
        with open(path, encoding="utf-8") as file:
            data = safe_load(file)
        self.title = data["title"]
        self.num_layers = data["layers"]
        self.loops: list[dict[str, list[str]]] = [dict() for _ in range(self.num_layers)]
        self.sections: dict[str, list[dict[str, list[str]]]] = data["sections"]
        for section_entries in self.sections.values():
            for entry in section_entries:
                entry_key: str; entry_loop: list[str]
                (entry_key, entry_loop), = entry.items()
                level_num, entry_char = read_entry_key(entry_key)
                self.loops[level_num][entry_char] = entry_loop
        self.index_memory: int = 0
        self.loop_memory: str = ""

    def dump(self, path: Path):
        obj = []
        print(path)
        for layer_num, layer in enumerate(self.loops):
            for loop in layer.items():
                obj.append({
                    "layer": layer_num,
                    "entry": loop[0],
                    "loop": loop[1]
                })
        with open(path, "w", encoding="utf-8") as file:
            json.dump(obj, file, ensure_ascii=False, indent=2)