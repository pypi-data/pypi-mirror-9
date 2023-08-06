# Peekaboo

Expose hardware info through HTTP.

# Install

Here are the instructions for a manuall install on CentOS 7.

```bash
sudo groupadd dmidecode
sudo useradd -M -G dmidecode peekaboo
sudo tee -a /etc/sudoers.d/dmidecode << EOT >/dev/null
%dmidecode ALL=(ALL) NOPASSWD:/usr/sbin/dmidecode
EOF
sudo yum install -y epel-release
sudo yum install -y libselinux-utils redhat-lsb python-devel python-pip gcc
git clone https://github.com/mickep76/peekaboo.git
sudo pip install -r peekaboo/requirements.txt
sudo cp peekaboo/peekaboo.conf /etc/peekaboo.conf
sudo cp peekaboo/peekaboo.py /usr/bin/peekaboo
sudo chmod +x /usr/bin/peekaboo
sudo mkdir /var/lib/peekaboo
sudo cp -r peekaboo/plugins /var/lib/peekaboo
```

# Run using Docker

You can quickly test it by running it inside a Docker container:


## Build docker image

```bash
docker build -t peekaboo:latest .
```

## Run docker image

```bash
docker run -d -p 5050:5050 --name=peekaboo peekaboo:latest
```

## Stop container:

```bash
docker stop peekaboo
```

# Query

Query using YAML:

```bash
curl -i http://<host>:5050/info
curl -i http://<host>:5050/status
```

Query using JSON:

```bash
curl -i -H "Accept: application/json" http://<host>:5050/info
curl -i -H "Accept: application/json" http://<host>:5050/status
```
