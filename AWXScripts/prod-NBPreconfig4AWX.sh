#!/bin/bash
echo "Start"
apt purge openssh-client -y
apt update
apt install ssh -y
if grep "user:x:" /etc/passwd; then
    sed -i 's/XDG_DESKTOP_DIR=[[:print:]]*$/XDG_DESKTOP_DIR=\"$HOME\/Desktop\"/' /home/user/user-dirs.dirs
    mkdir /home/user/Desktop
else
    useradd -m -s /bin/bash user
    mkdir /home/user/Desktop
    passwd -d user
fi
useradd -m -s /bin/bash awx
mkdir /home/awx/.ssh
cd /home/awx/.ssh
echo "ssh-rsa keystr" > authorized_keys
chown -R awx:awx /home/awx/.ssh
chmod -R 700 /home/awx/.ssh
echo "awx ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/awx
sed -i 's/#PubkeyAuthentication/PubkeyAuthentication/' /etc/ssh/sshd_config
systemctl restart ssh
mkdir /fallover
chmod 700 /fallover
chown root:root /fallover
echo "Finish"

