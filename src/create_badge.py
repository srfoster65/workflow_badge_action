"""
Script to construct and call a Badgen URL and fetch the resultant badge svg data
"""

from argparse import ArgumentParser
from os import environ
import requests
import logging
import uuid


OUTCOME_COLOUR_MAP = {
    "success": "green",
    "failure": "red",
    "cancelled": "grey",
    "skipped": "grey",
}


ACTION_OUTPUT = "badge"
BADGEN_URL = "http://badgen.net/badge"
logger = logging.getLogger(__name__)

def process_command_line_arguments():
    parser = ArgumentParser(description="Create a workflow badge")
    parser.add_argument(
        "-l", "--label",
        required=True,
        dest="label",
        help="The left hand badge text",
    )
    parser.add_argument(
        "-s", "--status",
        required=True,
        dest="status",
        help="The right hand badge text",
    )
    parser.add_argument(
        "-c", "--color", "--colour",
        dest="colour",
        help="The background status colour",
    )
    parser.add_argument(
        "-i", "--icon",
        dest="icon",
        default="github",
        help="The icon to use",
    )
    parser.add_argument(
        "-p", "--path",
        dest="path",
        required=True,
        help="The path to save the badge to",
    )
    
    return parser.parse_args()


def get_badge_colour(args):
    """Return background colour for status part of badge."""
    if args.colour:
        logger.info("Colour param provided")
        colour = args.colour
    elif args.status in OUTCOME_COLOUR_MAP:
        logger.info("Deriving colour from Status value")
        colour = OUTCOME_COLOUR_MAP[args.status]
    else:
        logger.info("Using default colour")
        colour = "blue"
    logger.info("Using colour: %s", colour)
    return colour

def get_badgen_badge(args):
    """Generate badge from badgen.net"""
    colour = get_badge_colour(args)
    url = f"{BADGEN_URL}/{args.label}/{args.status}/{colour}"
    params = {'icon': args.icon}
    response = requests.get(url, params=params)
    logger.info("Fetching badge from: %s", response.url)
    return response.text


def set_multiline_output(name, value):
    logger.info("%s=%s", name, value)
    with open(environ["GITHUB_OUTPUT"], "a") as fh:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)


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
