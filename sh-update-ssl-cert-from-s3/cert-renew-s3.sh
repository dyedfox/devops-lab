#!/bin/bash

CERT_PATH="/etc/ssl/private/pure-ftpd.pem"
ME_CERT_PATH="/etc/ssl/you_organization/ssl-you_organization.pem"

aws s3 cp s3://some-bucket-name/ssl/ssl-you_organization.pem $ME_CERT_PATH

ME_CERT_MOD_TIME=$(openssl x509 -text -noout -in $ME_CERT_PATH | grep "Not After :")
CERT_MOD_TIME=$(openssl x509 -text -noout -in $CERT_PATH |  grep "Not After :")

if [ "$ME_CERT_MOD_TIME" != "$CERT_MOD_TIME" ]; then
    cp $ME_CERT_PATH $CERT_PATH
    chmod 600 $CERT_PATH
    systemctl stop pure-ftpd-mysql && /usr/sbin/pure-uploadscript -B -r /etc/uploadscript.sh \
    && systemctl start pure-ftpd-mysql
    now=$(date +"%m-%d-%Y %T")
    echo "$now SSL Certificate Updated!" >> /home/you_organization/data/logs/uploadscript.log
fi
