version_cmd=''
download_url='http://www.rabbitmq.com/rabbitmq-signing-key-public.asc'
install_script="""
apt-key add rabbitmq-signing-key-public.asc
echo "deb http://www.rabbitmq.com/debian/ testing main" > /etc/apt/sources.list.d/rabbitmq.list
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y rabbitmq-server
"""