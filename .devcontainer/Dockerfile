FROM ubuntu:16.04
#ENV MYSQL_DATABASE DOCKERDB

# install dependencies
RUN sudo apt update
RUN sudo apt upgrade -y
RUN sudo apt install apache2 mariadb-server python3-pip
RUN sudo mkdir /var/www/customer_management
RUN sudo a2dismod mpm_event
RUN sudo a2enmod mpm_prefork cgi

# configure apache
RUN sudo cp config/000-default.conf /etc/apache2/sites-enabled/ 
RUN sudo service apache2 restart

# copy files correct location
RUN sudo cp -r ./ /var/www/customer_management/

# install python requirements
RUN pip install -r requirements.txt

# configure mariadb
RUN sudo mysql_secure_installation
