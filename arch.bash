#!/bin/bash

#set time
#locale
#resolv.conf
#fstab
#swap
#nomodeset and text grub
#modules
#mkinitcpio -p linux
#grub-mkconfig -o /boot/grub/grub.cfg
#grub-install

# picocom unrar

sudo systemctl disable man-db.time
sudo systemctl disable man-db.service


#TODO: fix journal size
install="pacman -S"

rmmod pcspkr
echo "blacklist pcspkr" > /etc/modprobe.d/nobeep.conf

#ADD ME
useradd exe
mkdir /home/exe
chown exe /home/exe
chmod 700 /home/exe

sudo gpasswd -a exe adm
sudo gpasswd -a exe wheel
sudo gpasswd -a exe audio
sudo gpasswd -a exe users
sudo gpasswd -a exe uucp   # /dev/ttyUSB0

#echo "enter root password"
#passwd root
#TODO: journal size

#SELECT MIRRORS
cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
sed '/^#\S/ s|#||' -i /etc/pacman.d/mirrorlist.backup
rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist
pacman -Syy

echo "upgrading world. This can trigger pacman upgrade"
pacman -Suy
echo "upgrading world"
pacman -Suy

#BASE
$install dhcpcd
$install rsync
$install net-tools
$install dnsutils
$install lm_sensors
$install ethtool
$install iptables
$install bridge-utils
$install parted
$install openssh
systemctl enable sshd
$install mosh
$install tmux
$install vim
$install atop
$install wget
$install aria2
$install sudo
$install dialog
$install mc
$install ntfs-3g
$install wpa_supplicant
$install rfkill
$install iw
$install tcpdump
$install openvpn
$install dosfstools
$install calc
$install pwgen
$intaall unzip

systemctl enable cronie
systemctl start cronie

#DEVEL
$install ghc
$install ipython
$install mercurial
$install git
$install strace
$install lsof

#X
$install xorg-xset
$install xorg-xhost
$install xorg-xprop
$install xorg-xrandr
$install xorg-xkill
$install xorg-xbacklight
$install xorg-setxkbmap
$install xorg-xset
$install xdotool
$install xf86-video-intel

$install terminus-font
$install alsa-utils
$install slock
$install xautolock
$install dmenu
$install fluxbox
$install rxvt-unicode
pkgbuilder -S xkbset
$install firefox
$install chromium
