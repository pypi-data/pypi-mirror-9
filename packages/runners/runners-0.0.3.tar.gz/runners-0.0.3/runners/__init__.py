"""Provide a common access point to all the utilities defined within.
"""

from runners import lock_helper

# In order to allow people to run:
# with runners.lock("..."):
#     do_something()
# we provide a member called `lock` which is a 'shortcut' to the `Lock` context
# manager class.
lock = lock_helper.Lock
