FROM ubuntu:16.04
#ENV MYSQL_DATABASE DOCKERDB

# install dependencies
RUN sudo apt update \
    && sudo apt upgrade -y \
    && sudo apt install apache2 mariadb-server \
    && sudo mkdir /var/www/customer_management \
    && sudo a2dismod mpm_event \
    && sudo a2enmod mpm_prefork cgi

# configure apache
RUN sudo cp config/000-default.conf /etc/apache2/sites-enabled/ \
    && sudo systemctl restart apache2

# copy files correct location
RUN sudo cp -r ./ /var/www/customer_management/

# install python requirements
RUN pip install -r requirements.txt --break-system-packages

# configure mariadb
RUN sudo mysql_secure_installation