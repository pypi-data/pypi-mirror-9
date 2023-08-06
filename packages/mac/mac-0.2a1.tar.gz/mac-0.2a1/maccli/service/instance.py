import os
import tempfile

import pexpect

import maccli.dao.api_instance


def list_instances():
    """
        List available instances in the account
    """
    return maccli.dao.api_instance.get_list()


def ssh_instance(servername, session_id, cmd = None):
    """
        ssh to an existing instance
    """
    instance = maccli.dao.api_instance.credentials(servername, session_id)

    if instance is not None:

        command_str = ""
        if cmd is not None:
            command_str = "%s" % cmd

        if instance['privateKey']:
            """ Authentication with private key """
            tmp_fpath = tempfile.mkstemp()
            try:
                with open(tmp_fpath[1], "wb") as f:
                    f.write(bytes(instance['privateKey']))
                command = "ssh %s@%s -i %s %s" % (instance['user'], instance['ip'], f.name, command_str)
                os.system(command)
            finally:
                os.remove(tmp_fpath[1])

        else:
            """ Authentication with password """
            command = "ssh %s@%s %s" % (instance['user'], instance['ip'], command_str)
            child = pexpect.spawn(command)
            i = child.expect(['.* password:', "yes/no"],  timeout=60)
            if i == 1:
                child.sendline("yes")
                child.expect('.* password:', timeout=60)

            child.sendline(instance['password'])
            child.interact()


def create_instance(cookbook_tag, deployment, location, servername, provider, release, branch, hardware, lifespan,
                    environments, hd, metadata = None):
    """
        List available instances in the account
    """
    return maccli.dao.api_instance.create(cookbook_tag, deployment, location, servername, provider, release, branch,
                                          hardware, lifespan, environments, hd, metadata)


def destroy_instance(servername, session_id):
    """

    Destroy the server

    :param servername:
    :return:
    """
    return maccli.dao.api_instance.destroy(servername, session_id)


def credentials(servername, session_id):
    """

    Gets the server credentials: public ip, username, password and private key

    :param servername:
    :param session_id:
    :return:
    """
    return maccli.dao.api_instance.credentials(servername, session_id)

def facts(servername, session_id):
    """

    Returns facts about the system

    :param servername:
    :param session_id:
    :return:
    """
    return maccli.dao.api_instance.facts(servername, session_id)

def log(servername, session_id):
    """

    Returns server logs

    :param servername:
    :param session_id:
    :return:
    """
    return maccli.dao.api_instance.log(servername, session_id)


def metadata(macfile_root, infrastructure_key, role_key, role):
    """
    Generate the json metadata to create an instance
    """
    metadata = macfile_root
    metadata['macfile_role_name'] = role_key
    metadata['macfile_infrastructure_name'] = infrastructure_key
    metadata['macfile_role_name'] = role_key
    if 'environment' in role.keys():
        metadata['environment_raw'] = role['environment']
    return metadata
