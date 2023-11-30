FROM alpine:latest as build

COPY 0001-honeypot-modifications.patch .

RUN apk add git gcc make libc-dev linux-headers \
	&& git clone https://github.com/redis/redis -b 3.0

RUN cd redis \
#	&& git apply ../0001-honeypot-modifications.patch \
	&& make -j`nproc`

FROM alpine:latest

WORKDIR /data

COPY --from=build /redis/src/redis-server .
COPY redis.conf module.so .

EXPOSE 6379

ENTRYPOINT ["/data/redis-server"] #, "/data/redis.conf"]
