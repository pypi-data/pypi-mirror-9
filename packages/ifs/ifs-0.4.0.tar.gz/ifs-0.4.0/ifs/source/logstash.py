version='1.4.2'
version_cmd='logstash version'
version_re='(\d+\.\d+\.\S+)'
download_url='https://download.elasticsearch.org/logstash/logstash/packages/debian/logstash_1.4.2-1-2c0f5a1_all.deb'
install_script="""
dpkg -i logstash_1.4.2-1-2c0f5a1_all.deb
"""
