"""Command-line interface. State is kept in a JSON file (default: inspection.json)."""
import argparse
import sys

from inspection import Inspection, InvalidInput, count_by_severity, limits_for

DEFAULT_FILE = "inspection.json"


def build_parser():
    p = argparse.ArgumentParser(prog="cli.py", description="Inspection Defect Logger")
    p.add_argument("--file", default=DEFAULT_FILE, help="state file (default: %(default)s)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("start", help="start a new inspection (overwrites the state file)")
    s.add_argument("--batch", required=True)
    s.add_argument("--sample-size", required=True)  # parsed by our own validator

    r = sub.add_parser("record", help="record a defect")
    r.add_argument("--severity", required=True, help="critical | major | minor")
    r.add_argument("--description", required=True)

    sub.add_parser("list", help="list recorded defects")
    sub.add_parser("verdict", help="show ACCEPT / REJECT")
    return p


def run(args):
    if args.command == "start":
        insp = Inspection(args.batch, args.sample_size)
        insp.save(args.file)
        print(f"Started inspection for batch {insp.batch_id} (sample size {insp.sample_size}).")
        return

    insp = Inspection.load(args.file)

    if args.command == "record":
        d = insp.record(args.severity, args.description)
        insp.save(args.file)
        print(f"Recorded {d.severity} defect: {d.description}")
    elif args.command == "list":
        if not insp.defects:
            print("No defects recorded.")
        for i, d in enumerate(insp.defects, 1):
            print(f"{i}. [{d.severity}] {d.description}")
    elif args.command == "verdict":
        counts = count_by_severity(insp.defects)
        major_limit, minor_limit = limits_for(insp.sample_size)
        print(f"Batch {insp.batch_id}, sample size {insp.sample_size}")
        print(f"  critical: {counts['critical']} (limit 0)")
        print(f"  major:    {counts['major']} (limit {major_limit})")
        print(f"  minor:    {counts['minor']} (limit {minor_limit})")
        print(f"Verdict: {insp.verdict()}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        run(args)
    except InvalidInput as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
