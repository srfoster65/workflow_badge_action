"""
Script to construct and call a Badgen URL and fetch the resultant badge svg data
"""

from argparse import ArgumentParser
from os import environ
import requests
import logging
import uuid


class InvalidStatusError(Exception):
    def __init__(self, status: str) -> None:
        super().__init__(f"Invalid status for workflow badge: {status}")
        

OUTCOME_MAP = {
    "success": {"status": "Passing", "colour": "green"},
    "failure": {"status": "Failing", "colour": "red"},
    "cancelled": {"status": "cancelled", "colour": "grey"},
    "skipped": {"status": "skipped", "colour": "grey"},
}


ACTION_OUTPUT = "badge"
GITHUB_OUTPUT = "GITHUB_OUTPUT"
BADGEN_URL = "http://badgen.net/badge"
DEFAULT_COLOUR = "blue"
DEFAULT_WORKFLOW_ICON = "github"
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
        "--label-colour",
        "--label-color",
        dest="labelColor",
        help="The background label colour",
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
        default=DEFAULT_COLOUR,
        help="The background status colour",
    )
    parser.add_argument(
        "-i",
        "--icon",
        dest="icon",
        default="",
        help="The icon to use",
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        help="The path to save the badge to. Store badge in environment variable if not set",
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="type",
        default="workflow",
        help="The type of badge to create - workflow, percentage, custom",
    )
    return parser.parse_args()


def get_workflow_badge_colour(args):
    """Return background colour for status part of badge."""
    # if args.colour:
    #     logger.info("Colour param provided: %s", args.colour)
    #     return args.colour
    colour = OUTCOME_MAP[args.status]["colour"]
    logger.info("Deriving colour from Status value: %s", colour)
    return colour
    raise InvalidStatusError(args.status)
    # logger.info("Using default colour: %s", DEFAULT_WORKFLOW_COLOUR)
    # return DEFAULT_WORKFLOW_COLOUR


def get_workflow_badge_status(args):
    """Return background colour for status part of badge."""
    status = OUTCOME_MAP[args.status]["status"]
    logger.info("Deriving badge status: %s => %s", args.status, status)
    return status

def get_badgen_badge(args):
    """Generate badge from badgen.net"""
    url = f"{BADGEN_URL}/{args.label}/{args.status}/{args.colour}"
    params = {
        key: getattr(args, key) for key in {"icon", "labelColor"} if getattr(args, key)
    }
    # params = {"icon": args.icon}
    logger.info("Fetching badge from: %s", url)
    response = requests.get(url, params=params)
    return response.text


def write_data(fh, name, value):
    delimiter = uuid.uuid1()
    print(f"{name}<<{delimiter}", file=fh)
    print(value, file=fh)
    print(delimiter, file=fh)


def write_github_output(name, value):
    if GITHUB_OUTPUT in environ:
        output_file = environ[GITHUB_OUTPUT]
    else:
        # For debugging outside of github
        output_file = "temp.txt"
        logger.info("GITHIB_OUTPUT not set. Using temp file")
    logger.info("Writing badge to github output: %s", output_file)
    with open(output_file, "w") as fh:
        write_data(fh, name, value)


def write_badge(path, badge_svg):
    if not path:
        # For debugging outside of github
        logger.info("GITHIB_OUTPUT not set and no path supplied. Using temp file")
        path = "temp.svg"
    logger.info("Saving badge to: %s", path)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(badge_svg)


def get_workflow_badge(args):
    logger.info("Generating workflow badge")
    if args.status in OUTCOME_MAP:
        setattr(args, "colour", get_workflow_badge_colour(args))
        setattr(args, "status", get_workflow_badge_status(args))
        setattr(args, "icon", DEFAULT_WORKFLOW_ICON)
        return get_badgen_badge(args)
    raise RuntimeError(f"Invalid status for workflow badge: {args.status}")


def is_percentage(value):
    logger.info("Converting status to integer")
    percent = int(value)
    return 0 <= percent <= 100


def get_percentage_colour(percentage):
    # todo Map percentage to colour
    # 0 = red
    # 100 = green
    return "blue"


def get_percentage_badge(args):
    logger.info("Generating percentage badge")
    if is_percentage(args.status):
        # todo Implement colour scaling
        setattr(args, "colour", get_percentage_colour(args.status))
        setattr(args, "icon", DEFAULT_WORKFLOW_ICON)
        return get_badgen_badge(args)
    raise RuntimeError(f"Invalid status for percentage badge: {args.status}")


def use_github_output(path):
    return GITHUB_OUTPUT in environ or path


def main():
    logging.basicConfig(level=logging.INFO)
    args = process_command_line_arguments()
    match args.type:
        case "workflow":
            badge_svg = get_workflow_badge(args)
        case "percentage":
            badge_svg = get_percentage_badge(args)
        case "custom":
            logger.info("Generating custom badge")
            badge_svg = get_badgen_badge(args)
        case _:
            raise RuntimeError(f"Invalid type: {args.type}")
    if use_github_output(args.path):
        write_github_output(ACTION_OUTPUT, badge_svg)
    else:
        write_badge(args.path, badge_svg)


if __name__ == "__main__":
    main()
