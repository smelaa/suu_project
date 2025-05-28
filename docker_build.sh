#!/bin/bash

docker build -t echo-app ./app
kind load docker-image echo-app:latest