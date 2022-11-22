#!/usr/bin/env bash
#
# FIXME: Need some scripts/build system for building and starting the modules
# This is just a temporary script for now

#MODULE=dtcc-module-hello-world
MODULE=dtcc-module-dtcc-builder

docker build -f $MODULE/Dockerfile .
