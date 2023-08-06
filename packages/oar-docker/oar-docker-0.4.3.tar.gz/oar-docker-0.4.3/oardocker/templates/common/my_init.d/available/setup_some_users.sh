#!/bin/sh
set -e

STAMP="/var/lib/container/stamps_oar_users_created"

create_users() {
    users="user1 user2 user3"

    for name in $users; do
        echo "Adding user $name..."
        useradd --user-group $name -s /bin/bash --no-create-home
        echo -n "$name:$name" | chpasswd
        usermod --append --groups sudo $name

        if [ $HOSTNAME = "frontend" ]; then
            ## We also need to copy configuration files (vimrc, bashrc, tmux.conf..)
            echo "Creating /home/$name"
            cp -rT /etc/skel /home/$name
            chown $name:$name -R /home/$name
        fi
    done
}


if [ -f "$STAMP" ]; then
    echo "OAR users already created"
else
    create_users
    touch $STAMP
fi
