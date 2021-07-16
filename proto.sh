#!/bin/bash
protoc -I=./ --python_out=./ ./object_detection/protos/*.proto
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
