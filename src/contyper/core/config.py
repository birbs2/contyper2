import configparser
from pathlib import Path

import yaml

from src.contyper.core.ruleset import Ruleset
class IniException(Exception):
    pass

class CTConfig(configparser.ConfigParser):
    def __init__(self):
        super().__init__()
        self.path = Path(__file__).parent.parent.resolve()
        self.ruleset = None
        self.read(self.joinpath("core", "options.ini"))
        self.reload_rs()

    def joinpath(self, *args):
        return self.path.joinpath(*args)

    def get_title(self, path: Path):
        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)["title"]

    def write_(self):
        with open(self.joinpath("core", "options.ini"), "w") as configfile:
            self.write(configfile)
        self.reload_rs()
        self.ruleset.dump(self.joinpath("rs.json"))

    def rel_from_presets(self, path: Path):
        return path.relative_to(self.joinpath("presets"))

    def rel_from_custom(self, path: Path):
        return path.relative_to(self.joinpath(self.get("Files", "rulesetdir")))

    def reload_rs(self):
        try:
            self.ruleset = Ruleset(Path(self.get("Files", "selectedfile")))
            self.set("Shortcuts", "layers", str(self.ruleset.num_layers))
        except OSError:
            self.set("Files", "selectedfile", str(self.joinpath("presets", "CT_ipa.yaml")))
            self.write_()


config = CTConfig()