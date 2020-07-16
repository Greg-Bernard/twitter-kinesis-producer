#!/bin/bash
#
# twitter_daemon      Startup script for twitter_daemon
#
### BEGIN INIT INFO
# Provides: twitter_daemon
# Required-Start: $local_fs
# Required-Stop: $local_fs
# Short-Description: start and stop twitter_daemon server
# Description: twitter_daemon is a Twitter content producer for AWS Kinesis
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

if [ -f /etc/sysconfig/twitter_daemon ]; then
        . /etc/sysconfig/twitter_daemon
fi

twitter_daemon=$(pwd)+twitter_daemon.py
prog=twitter_daemon
pidfile=${PIDFILE-/var/run/twitter_daemon.pid}
RETVAL=0

OPTIONS=""

start() {
        echo -n $"Starting $prog: "

        if [[ -f ${pidfile} ]] ; then
            pid=$( cat $pidfile  )
            isrunning=$( ps -elf | grep  $pid | grep $prog | grep -v grep )

            if [[ -n ${isrunning} ]] ; then
                echo $"$prog already running"
                return 0
            fi
        fi
        $twitter_daemon -p $pidfile $OPTIONS
        RETVAL=$?
        [ $RETVAL = 0 ] && success || failure
        echo
        return $RETVAL
}

stop() {
    if [[ -f ${pidfile} ]] ; then
        pid=$( cat $pidfile )
        isrunning=$( ps -elf | grep $pid | grep $prog | grep -v grep | awk '{print $4}' )

        if [[ ${isrunning} -eq ${pid} ]] ; then
            echo -n $"Stopping $prog: "
            kill $pid
        else
            echo -n $"Stopping $prog: "
            success
        fi
        RETVAL=$?
    fi
    echo
    return $RETVAL
}

reload() {
    echo -n $"Reloading $prog: "
    echo
}

# See how we were called.
case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status -p $pidfile $twitter_daemon
    RETVAL=$?
    ;;
  restart)
    stop
    start
    ;;
  force-reload|reload)
    reload
    ;;
  *)
    echo $"Usage: $prog {start|stop|restart|force-reload|reload|status}"
    RETVAL=2
esac

exit $RETVAL