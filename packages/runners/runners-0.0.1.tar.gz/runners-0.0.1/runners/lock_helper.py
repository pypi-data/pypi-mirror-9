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

    def __init__(self, path):
        client = get_zookeeper_client()
        logger.info("Starting zookeeper client...")
        self.path = path
        self.identifier = generate_identifier()
        logger.info("done")

        client.start()
        self.zookeeper_lock = kazoo_lock.Lock(client, self.path,
                                              self.identifier)
        # TODO: add a state listener

    def __enter__(self):
        logger.info("id={0}: waiting to acquire lock on {1}".format(
            self.identifier, self.path))
        self.zookeeper_lock.acquire(blocking=True)
        logger.info("acquired lock")
        return self

    def __exit__(self, type_, value, traceback):
        logger.info("releasing lock")
        self.zookeeper_lock.release()


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
