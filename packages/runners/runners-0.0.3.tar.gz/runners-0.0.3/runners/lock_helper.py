"""Provide a context manager that will acquire a lock (using zookeeper)
before running the given code.

with Lock("some-key"):
    do_something_exclusive()

If required, do_something_exclusive can be an infinite loop (a poller, or
an app).

Or it can simply be something that requires exclusive access.

It assumes an environment variable called ZOOKEEPER_HOSTS, which is a comma
separated string.

"""
import logging
import os
import socket
import uuid

import kazoo.client as kazoo_client
import kazoo.recipe.lock as kazoo_lock


logger = logging.getLogger("runners")


class Lock(object):

    def __init__(self, path, state_listener=None):
        client = get_zookeeper_client()
        logger.info("Starting zookeeper client...")
        self.path = path
        self.identifier = generate_identifier()
        logger.info("done")

        client.start()

        if state_listener:
            client.add_listener(state_listener)
        else:
            client.add_listener(default_state_listener)

        self.zookeeper_lock = kazoo_lock.Lock(client, self.path,
                                              self.identifier)
    def __enter__(self):
        logger.info("id={0}: waiting to acquire lock on {1}".format(
            self.identifier, self.path))
        self.zookeeper_lock.acquire(blocking=True)
        logger.info("acquired lock")
        return self

    def __exit__(self, type_, value, traceback):
        logger.info("releasing lock")
        self.zookeeper_lock.release()


def default_state_listener(state):
    logging.debug(u"**** state is now {0} ****".format(state))
    if state in [kazoo_client.KazooState.LOST,
                 kazoo_client.KazooState.SUSPENDED]:
        logging.error(u"Entered a bad state: {0}, exiting".format(state))
        # Zookeeper state is in an odd situation, we should exit ourselves to
        # ensure that the code doesn't run without being elected master.
        os._exit(0)


def generate_identifier():
    """Returns a string to be used as an identifier when waiting for a lock.
    """
    # While we use a uuid to ensure that it is globally unique, we also add
    # the hostname so that the identifier provides some human-readable info.
    return u"{0}-{1}".format(socket.gethostname(), uuid.uuid4().hex)


def get_zookeeper_client():
    zookeeper_hosts = os.getenv("ZOOKEEPER_HOSTS")
    if not zookeeper_hosts:
        raise LockException("No value found for  ZOOKEEPER_HOSTS env var")

    logger.info(u"zookeeper hosts={0}".format(zookeeper_hosts))
    return kazoo_client.KazooClient(hosts=zookeeper_hosts)


class LockException(Exception):
    pass
