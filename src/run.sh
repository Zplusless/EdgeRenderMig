sudo cp /home/edge/.Xauthority /root/.Xauthority

sudo rm node_log/*.log
sudo rm ue_log/*.csv
sudo rm ue_log/*.mp4

sudo python start_topology.py
