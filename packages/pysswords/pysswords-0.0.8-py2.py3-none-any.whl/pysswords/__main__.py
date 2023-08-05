import argparse
import logging
import os

from .cli import CLI

__version__ = "0.0.8"


def default_db():
    return os.path.join(os.path.expanduser("~"), ".pysswords")


def parse_args(cli_args=None):
    parser = argparse.ArgumentParser(prog="Pysswords")

    group_db = parser.add_argument_group("Database options")
    group_db.add_argument("-I", "--init", action="store_true",
                          help="create a new Pysswords database")
    group_db.add_argument("-D", "--database", default=default_db(),
                          help="specify path to database")

    group_cred = parser.add_argument_group("Credential options")
    group_cred.add_argument("-a", "--add", action="store_true",
                            help="add new credential")
    group_cred.add_argument("-g", "--get",
                            help="get credentials by name")
    group_cred.add_argument("-u", "--update",
                            help="update credentials")
    group_cred.add_argument("-r", "--remove",
                            help="remove credentials")
    group_cred.add_argument("-s", "--search",
                            help="search credentials. [regex supported]")
    group_cred.add_argument("-c", "--clipboard", action="store_true",
                            help="copy credential password to clipboard")
    group_cred.add_argument("-P", "--show-password", action="store_true",
                            help="show credentials passwords as plain text")

    group_runtime = parser.add_argument_group("Default options")
    group_runtime.add_argument("--version", action="version",
                               version="Pysswords {}".format(__version__),
                               help="Print version")

    args = parser.parse_args(cli_args)
    if args.clipboard and not args.get:
        parser.error('-g argument is required in when using -c')

    return args


def main(cli_args=None):
    args = parse_args(cli_args)

    interface = CLI(
        database_path=args.database,
        show_password=args.show_password,
        init=args.init
    )

    # credentials
    if args.add:
        interface.add_credential()
    elif args.get:
        if args.clipboard:
            interface.copy_to_clipboard(fullname=args.get)
        else:
            interface.get_credentials(fullname=args.get)
    elif args.search:
        interface.search_credentials(query=args.search)
    elif args.update:
        interface.update_credentials(fullname=args.update)
    elif args.remove:
        interface.remove_credentials(fullname=args.remove)

    if interface.display:
        interface.show_display()

from .db import CredentialExistsError, CredentialNotFoundError


if __name__ == "__main__":
    try:
        try:
            main()
        except CredentialExistsError as e:
            logging.error(str(e))
        except CredentialNotFoundError as e:
            logging.error(str(e))
        except ValueError as e:
            logging.error(str(e))
    except KeyboardInterrupt:
        print("")
