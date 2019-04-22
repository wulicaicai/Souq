#!/usr/bin/env bash
ps -ef|grep souq_product.py|grep -v grep|cut -c 9-15|xargs kill -s 9

rm -rf /tmp/souq_saudi.lock