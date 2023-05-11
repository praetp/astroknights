#!/bin/bash 
set -e
docker run -u $(id -u) -p 8080:8080 --rm -v /astrophotography/astroknights/tools/focus_analyzer/src/notebooks:/notebook \
-v /opt/spark:/opt/spark  -v /astrophotography/astroknights/tools/focus_analyzer/datasets:/datasets \
-e SPARK_HOME=/opt/spark -e ZEPPELIN_NOTEBOOK_DIR='/notebook'  --name zeppelin apache/zeppelin:0.10.1