"""
Script to construct and call a Badgen URL and fetch the resultant badge svg data
"""

from argparse import ArgumentParser
from os import environ
import requests
import logging
import uuid


OUTCOME_MAP = {
    "success": {"status": "Passing", "colour": "green"},
    "failure": {"status": "Failing", "colour": "red"},
    "cancelled": {"status": "cancelled", "colour": "grey"},
    "skipped": {"status": "skipped", "colour": "grey"},
}


ACTION_OUTPUT = "badge"
GITHUB_OUTPUT = "GITHUB_OUTPUT"
BADGEN_URL = "http://badgen.net/badge"
logger = logging.getLogger(__name__)


def process_command_line_arguments():
    parser = ArgumentParser(description="Create a workflow badge")
    parser.add_argument(
        "-l",
        "--label",
        required=True,
        dest="label",
        help="The left hand badge text",
    )
    parser.add_argument(
        "-s",
        "--status",
        required=True,
        dest="status",
        help="The right hand badge text",
    )
    parser.add_argument(
        "-c",
        "--color",
        "--colour",
        dest="colour",
        help="The background status colour",
    )
    parser.add_argument(
        "-i",
        "--icon",
        dest="icon",
        default="github",
        help="The icon to use",
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        help="The path to save the badge to. Store badge in environment variable if not set",
    )
    return parser.parse_args()


def get_badge_colour(args):
    """Return background colour for status part of badge."""
    if args.colour:
        logger.info("Colour param provided")
        colour = args.colour
    elif args.status in OUTCOME_MAP:
        logger.info("Deriving colour from Status value")
        colour = OUTCOME_MAP[args.status]["colour"]
    else:
        logger.info("Using default colour")
        colour = "blue"
    logger.info("Using colour: %s", colour)
    return colour


def get_badge_status(args):
    """Return background colour for status part of badge."""
    if args.status in OUTCOME_MAP:
        logger.info("Deriving badge status from status")
        return OUTCOME_MAP[args.status]["status"]
    logger.info("Using supplied status: %s", args.status)
    return args.status


def get_badgen_badge(args):
    """Generate badge from badgen.net"""
    colour = get_badge_colour(args)
    status = get_badge_status(args)
    url = f"{BADGEN_URL}/{args.label}/{status}/{colour}"
    params = {"icon": args.icon}
    response = requests.get(url, params=params)
    logger.info("Fetching badge from: %s", response.url)
    return response.text


def write_env_data(fh, name, value):
    delimiter = uuid.uuid1()
    print(f"{name}<<{delimiter}", file=fh)
    print(value, file=fh)
    print(delimiter, file=fh)


def set_multiline_output(name, value):
    if GITHUB_OUTPUT in environ:
        output_file = environ[GITHUB_OUTPUT]
    else:
        # For debugging outside of github
        output_file = "test.tmp"
        logger.info("GITHIB_OUTPUT not set. Using temp file:")
    logger.info("Writing badge to: %s", output_file)
    with open(output_file, "a") as fh:
        write_env_data(fh, name, value)


def write_badge(path, badge_svg):
    logger.info("Saving badge to: %s", path)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(badge_svg)


def main():
    logging.basicConfig(level=logging.INFO)
    args = process_command_line_arguments()
    badge_svg = get_badgen_badge(args)
    if args.path:
        write_badge(args.path, badge_svg)
    else:
        set_multiline_output(ACTION_OUTPUT, badge_svg)


if __name__ == "__main__":
    main()
