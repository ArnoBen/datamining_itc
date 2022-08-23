# To connect from local:

- add the key to repo:

```
export ROOT=/Users/shai/itc/DataMining/datamining_itc # local path to your repo
cp ~/Downloads/privkey.pem $ROOT/.ssh/
```


- And then:

```
 ssh -vv ubuntu@ec2-3-101-106-48.us-west-1.compute.amazonaws.com -i $ROOT/.ssh/privkey.pem
```

# On the server:

```
ubuntu@ip-172-31-29-60:~$ git clone git@github.com:ArnoBen/datamining_itc.git
Cloning into 'datamining_itc'...
ubuntu@ip-172-31-29-60:~/datamining_itc$ pwd
/home/ubuntu/datamining_itc

# follow the basic idea here: https://gist.github.com/Geoyi/d9fab4f609e9f75941946be45000632b

sudo apt-add-repository ppa:deadsnakes/ppa
sudo apt install software-properties-common
sudo apt install python3.9
virtualenv -p /usr/bin/python3.9 venv
virtualenv -p /usr/bin/python3.9 venv

source venv/bin/activate
which pip3
sudo apt-get install python3.9-distutils
pip3 --version
pip3 install -r requirements.txt
python3 main.py -c 2 -s

# setup mysql
sudo apt install mysql-client-core-5.7
sudo apt install mariadb-client-core-10.1


# opened a screen session, and
htop 
python main.py -c 1000 -o 2 -s

```

