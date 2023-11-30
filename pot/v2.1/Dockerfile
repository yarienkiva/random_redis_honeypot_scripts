FROM debian:buster

RUN apt update && apt install -y wget \
	&& wget https://debian.sipwise.com/debian-security/pool/main/r/redis/redis-tools_5.0.14-1+deb10u1_amd64.deb \
	&& wget https://debian.sipwise.com/debian-security/pool/main/r/redis/redis-server_5.0.14-1+deb10u1_amd64.deb \
	&& apt install -y ./redis-tools_5.0.14-1+deb10u1_amd64.deb \
	&& apt install -y ./redis-server_5.0.14-1+deb10u1_amd64.deb \
	&& rm redis-tools_5.0.14-1+deb10u1_amd64.deb \
	&& rm redis-server_5.0.14-1+deb10u1_amd64.deb

COPY system_module.so redis.conf /

ENTRYPOINT ["redis-server", "/redis.conf"]
