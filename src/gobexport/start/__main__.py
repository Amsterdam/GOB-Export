"""Start import

Requires one or more dataset description-files to run an import:

     python -m gobimport.start example/meetbouten.json
"""
import argparse

from gobcore.message_broker.config import EXPORT_QUEUE
from gobcore.message_broker import publish

parser = argparse.ArgumentParser(
    prog='python -m gobexport.start',
    description='Export one or more datasets',
    epilog='Generieke Ontsluiting Basisregistraties')

parser.add_argument('catalogue',
                    type=str,
                    help='the name of the data catalog (example: "meetbouten"')
parser.add_argument('collection',
                    type=str,
                    help='the name of the data collection (example: "meetbouten"')
parser.add_argument('filename',
                    type=str,
                    help='the name of the file to write the output to (example: "MBT_MEETBOUT.dat")')
parser.add_argument('destination',
                    nargs='?',
                    type=str,
                    default="Objectstore",
                    choices=["Objectstore", "File"],
                    help='destination, default is Objectstore')
args = parser.parse_args()

export_args = {
    "catalogue": args.catalogue,
    "collection": args.collection,
    "filename": args.filename,
    "destination": args.destination
}

publish(EXPORT_QUEUE, "export.start", export_args)
