# install apache
sudo apt-get install apache2 \Q

#expose public IP
sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 80 -j ACCEPT
sudo ufw allow 80
sudo ufw allow 80
sudo ufw reload

#apt update
sudo apt update

#install apache
sudo apt update \Q

#install wsgi and python essentials
sudo apt-get install libapache2-mod-wsgi python-dev \Q
sudo a2enmod wsgi \Q

#install python pip
sudo apt-get install python-pip \Q

#Python modules
sudo pip install flask
sudo pip install requests
sudo pip uninstall --yes Werkzeug
sudo pip install Werkzeug==0.16.0
sudo cp -f /var/www/html/AdvDistSystems/000-default.conf /etc/apache2/sites-enabled/000-default.conf

sudo service apache2 restart
sudo tail -f /var/log/apache2/error.log