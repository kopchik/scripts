#!/bin/bash
install="pacman -S"

rmmod pcspkr
echo "blacklist pcspkr" > /etc/modprobe.d/nobeep.conf

#ADD ME
useradd exe
mkdir /home/exe
chown exe /home/exe
chmod 700 /home/exe
gpasswd sudo gpasswd -a exe adm
gpasswd sudo gpasswd -a exe audio

#echo "enter root password"
#passwd root

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
$install sudo
$install dialog
$install mc
$install ntfs-3g
$install wpa_supplicant
$install iw
$install tcpdump
$install openvpn
$install dosfstools
$install calc
$install pwgen

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
$install xorg-xbacklight
$install terminus-font
$install xorg-xset
$install alsa-utils
$install slock
$install dmenu
$install fluxbox
$install rxvt-unicode
echo << EOF > /usr/local/bin/urxvtcd
#!/bin/sh
urxvtc "\$@"
if [ \$? -eq 2 ]; then
    urxvtd -q -f
    exec urxvtc "\$@"
fi
EOF
chmod +x /usr/local/bin/urxvtcd
$install firefox
$install chromium
