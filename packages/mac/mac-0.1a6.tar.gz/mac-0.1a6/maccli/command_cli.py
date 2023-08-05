import getpass
import ConfigParser
import sys
from os.path import join, expanduser

import service.auth
import service.instance
import service.provider
import maccli.service.configuration
from view.view_generic import show_error, show
import view.view_location
import view.view_instance
import view.view_cookbook
import view.view_generic
import maccli.view.view_hardware
from config import AUTH_SECTION, USER_OPTION, APIKEY_OPTION, MAC_FILE, EXCEPTION_EXIT_CODE


def help():
    view.view_generic.general_help()


def login():
    try:
        username = raw_input("Username or email: ")
        password = getpass.getpass()

        user, api_key = service.auth.authenticate(username, password)
        if api_key is not None:
            config = ConfigParser.ConfigParser()
            config.add_section(AUTH_SECTION)
            config.set(AUTH_SECTION, USER_OPTION, user)
            config.set(AUTH_SECTION, APIKEY_OPTION, api_key)
            with open(join(expanduser('~'), MAC_FILE), 'w') as cfgfile:
                config.write(cfgfile)
            print("Login succeeded!")

    except KeyboardInterrupt as e:
        show_error("")
        show_error("Authentication cancelled.")

    except Exception as e:
        show_error(e)
        sys.exit(EXCEPTION_EXIT_CODE)


def no_credentials():
    show("You need to login into Manageacloud.com")
    show()
    show("    mac login")
    show()
    show("If you do not have an account, you can register one at https://manageacloud.com/register")


def instance_list():
    try:
        json = service.instance.list_instances()
        view.view_instance.show_instances(json)

    except Exception as e:
        show_error(e)
        sys.exit(EXCEPTION_EXIT_CODE)


def instance_ssh(name, session_id):
    try:
        service.instance.ssh_instance(name, session_id)

    except Exception as e:
        show_error(e)
        sys.exit(EXCEPTION_EXIT_CODE)


def instance_create(cookbook_tag, deployment, location, servername, provider, release, branch, hardware, lifespan, environments):
    if cookbook_tag is None:
        view.view_instance.show_instance_create_help()


    elif location is None:
        locations_json = service.provider.list_locations(cookbook_tag, provider)
        if locations_json is not None:
            show()
            show("--location parameter not set. You must choose the location.")
            show()
            show("Available locations:")
            show()
            if len(locations_json):
                view.view_location.show_locations(locations_json)
                view.view_instance.show_instance_create_locations_example(cookbook_tag, locations_json[0]['id'])
            else:
                show("There is not locations available for configuration %s and provider %s" % (cookbook_tag, provider))

            view.view_instance.show_instance_help()
    elif deployment == "production" and hardware is None or \
                                    deployment == "testing" and provider is not "manageacloud" and hardware is None:
        hardwares = service.provider.list_hardwares(provider, location)
        show()
        show("--hardware not found. You must choose the hardware.")
        show()
        show("Available hardware:")
        show()
        view.view_hardware.show_hardwares(hardwares)
        if (len(hardwares) > 0):
            view.view_instance.show_create_example_with_parameters(cookbook_tag, deployment, location, servername,
                                                                   provider, release, branch, hardwares[0]['id'])
    else:
        """ Execute create instance """
        instance = service.instance.create_instance(cookbook_tag, deployment, location, servername, provider, release,
                                                    branch, hardware, lifespan, environments)
        if instance is not None:
            view.view_instance.show_instance(instance)


def instance_destroy_help():
    view.view_instance.show_instance_destroy_help()


def instance_ssh_help():
    view.view_instance.show_instance_ssh_help()


def instance_destroy(servername, session_id):
    instance = service.instance.destroy_instance(servername, session_id)
    if instance is not None:
        view.view_instance.show_instance(instance)


def instance_help():
    view.view_instance.show_instance_help()


def configuration_list():
    configurations = service.configuration.list_configurations()
    view.view_cookbook.show_configurations(configurations)


def configuration_search(keywords, show_url):
    configurations = service.configuration.search_configurations(keywords)
    if show_url:
        view.view_cookbook.show_configurations_url(configurations)
    else:
        view.view_cookbook.show_configurations(configurations)


def configuration_help():
    view.view_cookbook.show_configurations_help()
