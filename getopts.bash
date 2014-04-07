#!/bin/bash

OPTIND=1
l=""  # local URI
r=""  # remote URL
c="lzop"  # compression
while getopts "l:r:c:h" opt; do
  case $opt in
    l)
      l=$OPTARG
      ;;
    r)
      r=$OPTARG
      ;;
    c)
      c=$OPTARG
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

echo $l, $r, $c