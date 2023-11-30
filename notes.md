# useful ressources
https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf
https://blog.aquasec.com/headcrab-attacks-servers-worldwide-with-novel-state-of-art-redis-malware
https://blog.aquasec.com/redigo-redis-backdoor-malware
https://sleeplessbeastie.eu/2020/02/10/how-to-determine-which-key-was-used-to-login-with-openssh/

# notes
how to pwn:
- config set dbfilename + crontab/sshkey
- lua sandbox escape
- slaveof+module load

.
├── Dockerfile
├── main.py
├── redis.conf
├── sock_drawer
│   ├── AAA.BBB.CCC.DDD
│   │   └── redis.sock
 ...
│   └── XXX.YYY.ZZZ.WWW
│       └── redis.sock
└── system_module.so
