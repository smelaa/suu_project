#!/bin/bash

kubectl apply -f jaeger.yml
kubectl apply -f otel-collector.yml
kubectl apply -f otel-instrumentation.yml