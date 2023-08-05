
import subprocess
import sys
import time
import elpotrero.lib.util as elutil

# NOTE: MAKE SURE TO SET THE PYTHONPATH on root to include the elpotrero
# library, if you only set it in the default user library, then call sudo,
# python will NOT pick it up.
#
# HOWTO:
#
# http://stackoverflow.com/questions/7969540/
#    pythonpath-not-working-for-sudo-on-gnu-linux-works-for-root
#
# 1. put the elpotrero library in /usr/local/lib/py
# 2. add PYTHONPATH=$PYTHONPATH:/usr/local/lib/py to /etc/bash.bashrc
# 3. add PYTHONPATH to Default env_keep += "PYTHONPATH" in /etc/sudoers
# 4. remove Defaults !env_reset from sudoers if present


def execute(cmd_dict, cmd, name):
    info = elutil.execcommand(cmd_dict, cmd, name)
    print info['message']
    if info['retval'] != 0:
        sys.exit(info['retval'])


def main():
    nginx_cmd = "/etc/init.d/nginx"
    supervisor_cmd = "/etc/init.d/supervisor"

    nginx = dict()
    supervisor = dict()

    nginx['start'] = [nginx_cmd, "start"]
    nginx['stop'] = [nginx_cmd, "stop"]
    nginx['status'] = [nginx_cmd, "status"]

    supervisor['start'] = [supervisor_cmd, "start"]
    supervisor['stop'] = [supervisor_cmd, "stop"]
    supervisor['status'] = [supervisor_cmd, "status"]

    # before executing make sure the actual processes are running
    if subprocess.call(nginx['status']) == 0:
        execute(nginx, "stop", "nginx")
    if subprocess.call(supervisor['status']) == 0:
        execute(supervisor, "stop", "supervisor")

    # if we got to this stage then we should have exited the subprocess
    # however, sometimes it takes a second or two to kick out, in that case
    # check to see if it is still running, and if so, wait that extra
    # second or so
    if subprocess.call(nginx['status']) == 0 or subprocess.call(supervisor['status']) == 0:

        time.sleep(2)

    execute(nginx, "start", "nginx")
    execute(supervisor, "start", "supervisor")

main()
