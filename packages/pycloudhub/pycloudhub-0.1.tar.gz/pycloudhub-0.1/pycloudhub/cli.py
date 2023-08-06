"""
CloudHub API Wrapper command line interface.
"""
import argparse
import os

from pycloudhub import CloudHubApp



# environment variable names
CLOUDHUB_USER = 'CLOUDHUB_USER'
CLOUDHUB_PASS = 'CLOUDHUB_PASS'
CLOUDHUB_APP = 'CLOUDHUB_APP'


def create_parser():

    # check for the environment variables
    user_name = os.environ[CLOUDHUB_USER] if CLOUDHUB_USER in os.environ else None
    user_pass = os.environ[CLOUDHUB_PASS] if CLOUDHUB_PASS in os.environ else None
    app_name = os.environ[CLOUDHUB_APP] if CLOUDHUB_APP in os.environ else None

    parser = argparse.ArgumentParser(
        prog='pycloudhub',
        description='CloudHub API Wrapper',
        epilog='For more information on each command: cloudhub {command} -h'
    )
    subparsers = parser.add_subparsers(title='commands')

    credentials_parser = argparse.ArgumentParser(add_help=False)

    credentials_parser.add_argument(
        '-u', '--username', default=user_name, required=False if user_name else True
    )
    credentials_parser.add_argument(
        '-p', '--password', default=user_pass, required=False if user_pass else True
    )
    credentials_parser.add_argument(
        '-a', '--app-name', default=app_name, required=False if app_name else True
    )

    app_info_parser = subparsers.add_parser(
        'info',
        help='Retrieves the metadata associated with a CloudHub application',
        parents=[credentials_parser],
        description='Retrieves application metadata'
    )
    app_info_parser.set_defaults(func=get_application_info)

    deploy_parser = subparsers.add_parser(
        'deploy',
        help='Deploys the Mule application archive to CloudHub',
        parents=[credentials_parser],
        description='Deploys application archive to CloudHub'
    )
    deploy_parser.add_argument(
        '-f', '--file', required=True, dest='file_name'
    )
    deploy_parser.set_defaults(func=deploy_application)

    return parser


def _create_cloud_hub_app(args):
    return CloudHubApp(args.app_name, args.username, args.password)


def get_application_info(args):
    app = _create_cloud_hub_app(args)
    print(app.get_app_info())


def deploy_application(args):
    app = _create_cloud_hub_app(args)
    with open(args.file_name, 'rb') as file:
        app.deploy(file)

    print('File {0} was successfully uploaded to CloudHub'.format(os.path.basename(args.file_name)))


def main():
    parser = create_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()


if __name__ == '__main__':
    main()