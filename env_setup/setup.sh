sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak
sudo cp ./sources.list /etc/apt/sources.list



sudo apt update

sudo apt-get install -y git ssh python3-pip curl net-tools vim 

sudo ln -s /usr/bin/python3 /usr/bin/python
sudo ln -s /usr/bin/pip3 /usr/bin/pip

# # config pip
# mininet run as root, so only sudo pip works.
sudo pip install pip -U
sudo pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
sudo pip install flask requests ffmpeg-python docker numpy gunicorn

# opencv-python
sudo apt-get  install -y python3-opencv ffmpeg


setup_path=`pwd`

echo -e "########################################################"
echo -e "                  install gtp5g"
echo -e "########################################################"
sleep 1


cd ~
git clone https://github.com/PrinzOwO/gtp5g.git
cd gtp5g
make clean && make
sudo make install


echo -e "########################################################"
echo -e "                  install libgtp5gnl"
echo -e "########################################################"
sleep 1

cd ~
sudo apt-get -y install bridge-utils libmnl-dev automake
sudo apt-get -y install bison flex binutils build-essential autoconf libtool pkg-config automake

git clone https://github.com/PrinzOwO/libgtp5gnl.git

sleep 1

cd libgtp5gnl
autoreconf -iv && ./configure --prefix=`pwd`

make

cd tools
echo 'export PATH=$PATH:'$(pwd) >> ~/.bashrc
source ~/.bashrc

echo -e "########################################################"
echo -e "                  install mininet"
echo -e "########################################################"
sleep 2


# sudo rm /usr/bin/python
# sudo ln -s /usr/bin/python3 /usr/bin/python


cd ~
git clone git://github.com/mininet/mininet.git
cd mininet

git checkout -b mininet-2.3.0 2.3.0
PYTHON=python3 ~/mininet/util/install.sh -a


# git checkout 2.2.2
# cp $setup_path/modified_install_mininet.sh ~/mininet/util/
# bash ~/mininet/util/modified_install_mininet.sh -a




echo -e "########################################################"
echo -e "                  change branch of pox"
echo -e "########################################################"
sleep 2

cd ~/pox
git checkout eel 
cp $setup_path/../load_balancer/5g_loadbalancer.py ~/pox/ext/


echo -e "---------------------------------------------------------"
echo -e "                  please reopen the shell!!!!"
echo -e "---------------------------------------------------------"

cd ~
