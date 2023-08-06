"""
"""
import collections

import ansible.playbook
from ansible import callbacks as ansible_callbacks
from ansible import utils

from . import logging

class PlayBook(object):
    @classmethod
    def factory(cls, playbook, inventory=None, stats=None, callbacks=None,
                runner_callbacks=None, check=True, host_list=None, limit=None,
                logger=None):
        """
        :inventory: Ansible Inventory instance to setup.
        :limit: A dictionary or list of dictionaries limiting the PlayBook.
            Example:
            {"hostname": "server", "ip": "1.2.3.4"}
            or
            [{"hostname": "server1", "ip": "1.2.3.4"}, 
             {"hostname": "server2", "ip": "1.2.3.5"}]
        """
        if logger:
            logging.use_logger(logger)
        deps = PlayBook._setup(playbook, inventory, stats, callbacks,
                               runner_callbacks, host_list, limit)
        return ansible.playbook.PlayBook(
            playbook=deps.playbook,
            inventory=deps.inventory,
            stats=deps.stats,
            callbacks=deps.callbacks,
            runner_callbacks=deps.runner_callbacks,
            check=check)

    @classmethod
    def _setup(cls, playbook, inventory, stats, callbacks, runner_callbacks,
              host_list, limit):
        """
        Setup dependencies for the Ansible PlayBook and return them
        in a namedtuple.
        """
        deps = collections.namedtuple("Dependencies",
                                      ["playbook", "inventory", "stats",
                                       "callbacks", "runner_callbacks"])
        deps.playbook = playbook
        if stats is None:
            deps.stats = ansible_callbacks.AggregateStats()
        else:
            deps.stats = stats
        if callbacks is None:
            deps.callbacks = ansible_callbacks.PlaybookCallbacks(
                verbose=utils.VERBOSITY)
        else:
            deps.callbacks = callbacks
        if runner_callbacks is None:
            deps.runner_callbacks = ansible_callbacks.PlaybookRunnerCallbacks(
                stats,
                verbose=utils.VERBOSITY)
        else:
            deps.runner_callbacks = runner_callbacks
        if inventory is None:
            deps.inventory = ansible.inventory.Inventory(host_list=host_list)
            if limit:
                PlayBook._setup_inventory_limit(deps.inventory, limit)
        else:
            deps.inventory = inventory
        return deps

    @classmethod
    def _setup_inventory_limit(cls, inventory, limit):
        """
        Setup and limit hosts using inventory and limit.
        :inventory: Ansible Inventory instance to setup.
        :limit: A dictionary or list of dictionaries limiting the PlayBook.
            Example:
            {"hostname": "server", "ip": "1.2.3.4"}
            or
            [{"hostname": "server1", "ip": "1.2.3.4"}, 
             {"hostname": "server2", "ip": "1.2.3.5"}]
        """
        if isinstance(limit, dict):
            inventory.subset(limit["hostname"])
            PlayBook._setup_host(inventory, limit)
        elif isinstance(limit, collections.Iterable):
            hostnames = ",".join([l["hostname"] for l in limit])
            inventory.subset(hostnames)
            for l in limit:
                PlayBook._setup_host(inventory, l)

    @classmethod
    def _setup_host(cls, inventory, limit):
        """
        Check host and setup variables so limit/subset behaves
        as expected.
        """
        host = inventory.get_host(limit["hostname"])
        if host and host.vars:
            host.vars["ansible_ssh_host"] = limit["ip"]
        else:
            raise Exception("The host (%s) is not in the "
                            "Ansible inventory file %s." %
                            (host, inventory.host_list))
