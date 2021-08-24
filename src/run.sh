sudo cp /home/edge/.Xauthority /root/.Xauthority

sudo rm node_log/*.log
sudo rm ue_log/*.csv

sudo python start_topology.py
