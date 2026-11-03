"""Core logic for the Inspection Defect Logger: data model and verdict rule."""
import json
from dataclasses import dataclass, field

SEVERITIES = ("critical", "major", "minor")

# (sample size at least, major limit, minor limit) -- sorted ascending.
LIMITS = [
    (1, 0, 1),
    (15, 1, 4),
    (50, 4, 8),
    (180, 7, 15),
    (700, 14, 30),
]


class InvalidInput(ValueError):
    """Raised for any bad user input (sample size, severity, batch id...)."""


def parse_sample_size(value):
    """Return a valid sample size as int, or raise InvalidInput (R4)."""
    if isinstance(value, bool):
        raise InvalidInput("Sample size must be a whole number.")
    if isinstance(value, str):
        try:
            value = int(value.strip())
        except ValueError:
            raise InvalidInput(f"Sample size must be a whole number, got {value!r}.")
    if not isinstance(value, int):
        raise InvalidInput("Sample size must be a whole number.")
    if value < 1:
        raise InvalidInput(f"Sample size must be at least 1, got {value}.")
    return value


def limits_for(sample_size):
    """R1: the row with the largest 'at least' <= sample size. No interpolation."""
    sample_size = parse_sample_size(sample_size)
    chosen = LIMITS[0]
    for row in LIMITS:
        if row[0] <= sample_size:
            chosen = row
    return chosen[1], chosen[2]  # (major_limit, minor_limit)


def compute_verdict(sample_size, defects):
    """R2/R3: returns 'ACCEPT' or 'REJECT'. `defects` is a list of Defect."""
    major_limit, minor_limit = limits_for(sample_size)
    counts = count_by_severity(defects)
    if (
        counts["critical"] >= 1
        or counts["major"] > major_limit   # strictly greater: equal is OK
        or counts["minor"] > minor_limit
    ):
        return "REJECT"
    return "ACCEPT"


def count_by_severity(defects):
    counts = {s: 0 for s in SEVERITIES}
    for d in defects:
        counts[d.severity] += 1
    return counts


@dataclass
class Defect:
    severity: str
    description: str

    def __post_init__(self):
        self.severity = str(self.severity).strip().lower()
        if self.severity not in SEVERITIES:
            raise InvalidInput(
                f"Severity must be one of {', '.join(SEVERITIES)}, got {self.severity!r}."
            )
        self.description = str(self.description).strip()
        if not self.description:
            raise InvalidInput("Defect description must not be empty.")


@dataclass
class Inspection:
    batch_id: str
    sample_size: int
    defects: list = field(default_factory=list)

    def __post_init__(self):
        self.batch_id = str(self.batch_id).strip()
        if not self.batch_id:
            raise InvalidInput("Batch ID must not be empty.")
        self.sample_size = parse_sample_size(self.sample_size)

    def record(self, severity, description):
        defect = Defect(severity, description)
        self.defects.append(defect)
        return defect

    def verdict(self):
        return compute_verdict(self.sample_size, self.defects)

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "sample_size": self.sample_size,
            "defects": [vars(d) for d in self.defects],
        }

    @classmethod
    def from_dict(cls, data):
        try:
            insp = cls(data["batch_id"], data["sample_size"])
            for d in data.get("defects", []):
                insp.record(d["severity"], d["description"])
        except (KeyError, TypeError) as e:
            raise InvalidInput(f"Saved inspection file is malformed: {e!r}")
        return insp

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path):
        try:
            with open(path, encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        except FileNotFoundError:
            raise InvalidInput(f"No inspection found at {path}. Run 'start' first.")
        except json.JSONDecodeError:
            raise InvalidInput(f"{path} is not valid JSON.")
