#!/bin/bash

#TODO: check what will happen on overquota
#TODO: what happen if connection brake?

PASSWORD="file:/root/.backup_enc_pass"
TAR="tar --atime-preserve --numeric-owner -cjf -"
ENCRYPT="openssl enc -aes-256-cbc -salt -pass $PASSWORD"
SSHFS="sshfs -o Ciphers=arcfour"

## EXE BASHLIB VERSION=1.5 ##############################
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:$PATH
color_yellow() { echo -ne "\033[33;1m"; }
color_red() { echo -ne "\033[31;1m"; }
color_white() { echo -ne "\033[00m"; }
color_green() { echo -ne "\033[1;32m"; }

print_red() { color_red; echo -e "$*"; color_white; }
print_yellow() { color_yellow; echo -e "$*"; color_white; }
print_green() { color_green; echo -e "$*"; color_white; }

print_debug() { if [[ $DEBUG != 0 ]]; then echo -e "$*"; fi }

die() { print_red "$*"; exit 1; }


#stolen from http://www.linuxjournal.com/content/use-bash-trap-statement-cleanup-temporary-files
declare -a on_exit_items

function on_exit() {
    for i in "${on_exit_items[@]}"
    do
        echo "on_exit: $i"
        eval $i
    done
}

function add_on_exit() {
    local n=${#on_exit_items[*]}
    on_exit_items[$n]="$*"
    if [[ $n -eq 0 ]]; then
        echo "Setting trap"
        trap on_exit EXIT
    fi
}
## END OF BASHLIB########################################

LOCALPATH=""
REMOTEURL=""
COMPRESSION="lzop"  # compression
OPTIND=1
while getopts "l:r:c:h:d:" opt; do
  case $opt in
    l)
      LOCALPATH=$OPTARG
      ;;
    r)
      REMOTEURL=$OPTARG
      ;;
    c)
      COMPRESSION=$OPTARG
      ;;
    d)
      DEBUG=1
      ;;
    h)
      echo "Usage:"
      echo "  $0 -l <local URI> -r <remote URL> [-c zip]"
      echo "  example: $0 -l /home -r mybackups@backup.org: -c lzop"
      exit
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

if [[ -z "$LOCALPATH" || -z "$REMOTEURL" ]]; then
    die "I need two arguments: -l localpath-r remotepath"
fi

MNT="/mnt/`echo $REMOTEURL | cut -d: -f1 | cut -d@ -f2`"
OUTFILE="$MNT/`basename $LOCALPATH`_`date +%F`"
print_debug "OUTFILE: $OUTFILE"

print_debug "mounting sshfs"
if [ !  -d $MNT ]; then
    print_green "creating $MNT"
    mkdir -p $MNT || die "cannot make a mount mount"
fi
$SSHFS $REMOTEURL $MNT || die "cannot mount sshfs"
add_on_exit fusermount -u $MNT

print_debug "uploading file"
test -s "$OUTFILE" && die "output file already exists: \"$OUTFILE\""
CMD="$TAR $LOCALPATH | $ENCRYPT > "$OUTFILE" || die \"openssl error\""
print_debug "$CMD"
$CMD
print_debug "syncing filesystems"
sync # this will never hurt (c) slackware. Actually it can :)