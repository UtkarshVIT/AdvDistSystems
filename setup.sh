#https://raw.githubusercontent.com/UtkarshVIT/AdvDistSystems/production/setup.sh

#expose public IP
sudo iptables -I INPUT -p tcp -s 0.0.0.0/0 --dport 80 -j ACCEPT
sudo ufw allow 80
sudo ufw allow 80
sudo ufw reload
sudo apt update -y

sudo apt-get update -y
# install apache
sudo apt-get install apache2 -y
#install wsgi and python essentials
sudo apt-get install libapache2-mod-wsgi python-dev -y
sudo a2enmod wsgi -y

#install python pip
sudo apt-get install python-pip -y

sudo git clone -b production https://github.com/UtkarshVIT/AdvDistSystems.git /var/www/html/AdvDistSystems

#Python modules
sudo pip install flask
sudo pip install requests
sudo pip install Flask-Caching
#sudo pip install python-memcached
#sudo pip uninstall --yes Werkzeug
#sudo pip install Werkzeug==0.16.0

sudo cp -f /var/www/html/AdvDistSystems/000-default.conf /etc/apache2/sites-enabled/000-default.conf

sudo a2enmod wsgi -y
sudo service apache2 restart
sudo tail -f /var/log/apache2/error.log

#'{"nodes":[{"ip":"172.23.0.3:5000","key":3000},{"ip":"172.23.0.4:5000","key":6000},{"ip":"172.23.0.5:5000","key":9000}]}'