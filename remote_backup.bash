#!/bin/bash

#TODO: check whatss happend on overquota
#DONE:
#what happend if connection broke? - nothing good

BASE="/mnt/dim13"
REMOTE="exe@dim13.org"
PASSWORD="file:/root/.backup_enc_pass"

## EXE BASHLIB VERSION=1.5 ##############################
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:$PATH
color_yellow() { echo -ne "\033[33;1m"; }
color_red() { echo -ne "\033[31;1m"; }
color_white() { echo -ne "\033[00m"; }
color_green() { echo -ne "\033[1;32m"; }

print_red() { color_red; echo -e "$*"; color_white; }
print_yellow() { color_yellow; echo -e "$*"; color_white; }
print_green() { color_green; echo -e "$*"; color_white; }

print_debug() { if [ $DEBUG != 0 ]; then echo -e "$*"; fi }

die() { print_red "$*"; exit 1; }
doReboot() { print_red "$*"; shutdown -r now; }

getLinHash() { python -c "import crypt; print crypt.crypt(\"${1}\",\"\$1\$`pwgen -n -c 8 1`\$\")"; }

#stolen from http://www.linuxjournal.com/content/use-bash-trap-statement-cleanup-temporary-files
declare -a on_exit_items

function on_exit()
{
    for i in "${on_exit_items[@]}"
    do
        echo "on_exit: $i"
        eval $i
    done
}

function add_on_exit()
{
    local n=${#on_exit_items[*]}
    on_exit_items[$n]="$*"
    if [[ $n -eq 0 ]]; then
        echo "Setting trap"
        trap on_exit EXIT
    fi
}
## END OF BASHLIB########################################


#SANITY CHECK
INFILE="$1"
if [ "$INFILE" == "-" ]; then
    test $# -ne 2 && die "this script accepts 2 parameters ('-' and dst filename)"
    MODE="stdin"
    OUTFILE="${BASE}/${2}-`date +%F`"
else
    test $# -ne 1 && die "this script accepts only 1 parameter (filename to copy)"
    MODE="copy"
    test -f "$INFILE"  || die "can't find file \"$INFILE\""
    OUTFILE="${BASE}/`basename $1`_enc-`date +%F`"
fi


#REMOTE MOUNT
sshfs -C arcfour $REMOTE: $BASE || die "cant mount sshfs"
add_on_exit fusermount -u $BASE || die "cant unmount sshfs"


#UPLOAD FILE
test -s "$OUTFILE" && die "output file already exists: \"$OUTFILE\""
#to decode use "openssl enc -d -aes-256-cbc -in file.enc -out file.dec"
if [ "$MODE" == "copy" ]; then
    openssl enc -aes-256-cbc -salt -pass $PASSWORD -in "$INFILE" -out "$OUTFILE" || die "openssl error"
    #VERIFY UPLOAD
    FILESIZE=$(stat -c%s "$INFILE")
    UPLOADSIZE=$(stat -c%s "$OUTFILE") || die "upload file error"
    echo "ORIG: $FILESIZE; UPLOAD: $UPLOADSIZE"
    if [ $UPLOADSIZE -lt $FILESIZE ]; then
        die "uploaded file less than orig. At least check quota."
    fi
else
    cat | openssl enc -aes-256-cbc -salt -pass $PASSWORD > "$OUTFILE" || die "openssl error"
fi


sync # this will never hurt (c) slackware. Actually it can :)