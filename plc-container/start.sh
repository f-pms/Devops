#!/bin/sh

/usr/local/bin/cloudflared access tcp --hostname plc-dev01.ngochuy.xyz --url 0.0.0.0:9110 &
/usr/local/bin/cloudflared access tcp --hostname plc-dev02.ngochuy.xyz --url 0.0.0.0:9115
