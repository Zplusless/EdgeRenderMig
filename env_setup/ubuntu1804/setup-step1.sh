sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak
sudo cp ./sources.list /etc/apt/sources.list
sudo apt update

sudo apt-get install -y git ssh python3-pip curl net-tools vim

# # config pip
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install flask requests ffmpeg-python docker numpy

# opencv-python
sudo apt-get  install -y python3-opencv ffmpeg

# linux-core 5.0.0-23
sudo apt install -y linux-headers-5.0.0-23-generic linux-image-5.0.0-23-generic

# update linux core config
sudo update-grub

echo -e "########################################################"
echo -e "       plese reboot linux and run setup-step2.sh"
echo -e "########################################################"