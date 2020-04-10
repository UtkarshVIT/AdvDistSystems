#expose public IP
sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 80 -j ACCEPT
sudo ufw allow 80
sudo ufw allow 80
sudo ufw reload

#apt update
sudo apt update

#install apache
sudo apt update /Q

#install wsgi and python essentials
sudo apt-get install libapache2-mod-wsgi python-dev
sudo a2enmod wsgi

#install python pip
sudo apt-get install python-pip

#Python modules
sudo pip install flask
sudo pip install requests
sudo pip uninstall Werkzeug
sudo pip install Werkzeug==0.16.0
sudo cp -f /home/usharma2/AdvDistSystems/000-default.conf /etc/apache2/sites-enabled/000-default.conf

sudo service apache2 restart
sudo tail -f /var/log/apache2/error.log