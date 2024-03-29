#!/bin/bash

customExit(){
    msg="$1"
    code="$2"
    if [ -z "$1" ]; then
        msg="Unknown Error $code"
    elif [ ! -z "$code" ]; then
        if [ $2 -ne 0 ]; then
            msg="Error code $code: $msg"
        else
            msg="Info: $msg"
        fi
    fi
    xmessage -buttons Ok:0 -default Ok -nearmouse "$msg"
    exit $code
}

if [ "@$HOSTNAME" = "@linuxtower" ]; then
    if [ "@$USER" = "@maria" ]; then
        mkdir -p ~/git
        code=$?
        if [ $code -ne 0 ]; then
            customExit "'mkdir -p ~/git' failed." $code
        fi
        cd ~/git
        if [ $code -ne 0 ]; then
            customExit "'cd ~/git' failed." $code
        fi
        if [ ! -d "preinstall-linuxtower-maria" ]; then
            # Run the first-time setup.
            # URL="https://raw.githubusercontent.com/poikilos/preinstall-linuxtower-maria/main/always_add/home/maria/Projects/BackupNow/BackupNow.sh"
            # wget -O ~/Projects/BackupNow/BackupNow.sh "$URL"
            URL="https://github.com/poikilos/preinstall-linuxtower-maria.git"
            if [ ! -f "`command -v git`" ]; then
                customExit "Error: git is not installed but it is required in order to install preinstall-linuxtower-maria."
            fi
            echo "* installing preinstall-linuxtower-maria..."
            git clone $URL preinstall-linuxtower-maria
            code=$?
            if [ $code -ne 0 ]; then
                customExit "Installing preinstall-linuxtower-maria failed." $code
            fi
            rsync -rt ~/git/preinstall-linuxtower-maria/always_add/home/maria/Projects/BackupNow/ /home/maria/Projects/BackupNow
            if [ $code -ne 0 ]; then
                customExit "Installing BackupNow failed." $code
            fi
            xmessage -buttons Ok:0 -default Ok -nearmouse "Installing settings succeeded. Press OK to run BackupNow."
            chmod +x /home/maria/Projects/BackupNow/BackupNow.sh
            /home/maria/Projects/BackupNow/BackupNow.sh --no-management
            exit 0
            # ^ signal to BackupNow.sh that this operation ran a backup and that it (version that called this script) doesn't run it
            #   nor cause infinite recursion!
        else
            # First-time setup was already complete, so run the cross-update & backup.
            cd ~/git/preinstall-linuxtower-maria
            if [ $code -ne 0 ]; then
                customExit "'cd ~/git/preinstall-linuxtower-maria' failed." $code
            fi
            echo "* updating preinstall-linuxtower-maria..."
            git pull
            rsync -rt ~/git/preinstall-linuxtower-maria/always_add/home/maria/Projects/BackupNow/ /home/maria/Projects/BackupNow
            # ^ The shell version of BackupNow is a temporary solution and is not in the BackupNow repo
            #   (It is in the preinstall-linuxtower-maria repo).
            if [ $code -ne 0 ]; then
                xmessage -buttons Ok:0 -default Ok -nearmouse "Updating BackupNow failed. The old backup should detect this and continue." $code
                #chmod +x /home/maria/Projects/BackupNow/BackupNow.sh
                #/home/maria/Projects/BackupNow/BackupNow.sh
                exit $code
            fi
            # xmessage -buttons Ok:0 -default Ok -nearmouse "Updating settings succeeded. Press OK to run BackupNow."
            echo "Updating settings succeeded. The BackupNow script will now run."
            chmod +x /home/maria/Projects/BackupNow/BackupNow.sh
            export UPDATE=false
            /home/maria/Projects/BackupNow/BackupNow.sh --no-management
            exit 0
            # ^ signal to BackupNow.sh that this operation ran a backup and that it
            #   (The version of BackupNow.sh that called this script) doesn't continue
            #   to the backup code nor the code that calls this (manage.sh),
            #   which would cause infinite recursion!
        fi
        #if [ $? -ne 0 ]; then
        #    xmessage -buttons Ok:0 -default Ok -nearmouse "Error: backup $DST_PROFILE/Documents failed. Try re-inserting $targetvol."
        #    ( speaker-test -t sine -f 1000 )& pid=$! ; sleep 0.25s ; kill -9 $pid
        #    ( speaker-test -t sine -f 1000 )& pid=$! ; sleep 0.25s ; kill -9 $pid
        #    ( speaker-test -t sine -f 1000 )& pid=$! ; sleep 0.25s ; kill -9 $pid
        #    exit 1
        #fi
    fi

fi
customExit "Info: There are no actions for $USER at $HOSTNAME." 1
exit 1
# ^ Return non-zero to signal the
#   [bash version of BackupNow](https://raw.githubusercontent.com/poikilos/preinstall-linuxtower-maria/main/always_add/home/maria/Projects/BackupNow/BackupNow.sh)
#    to continue the backup since this one is not yet implemented.
