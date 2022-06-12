#!/bin/sh
ESA=$(echo $ELASTICSEARCH_ADDRESS | sed -E 's/,/ /g; s/\]/ /g; s/\[/ /g; s/"/ /g; s/''/ /g')
if [ "$ESA" == "" ];  then
  exit 1
fi
if [ "$ETL_INITIAL_LOAD_WAIT_SECONDS" == "" ];  then
  exit 1
fi
SLEEPS=0
while [ "$SLEEPS" -lt "$ETL_INITIAL_LOAD_WAIT_SECONDS" ]
do
  for EA in $(echo $ESA)
    do
      COUNT=$(curl "$EA/_cat/count" 2>/dev/null | awk '{print $3}')
      if echo $COUNT | grep -Eq '^[0-9]+$' ; then
        if [ "$COUNT" -ge "$ETL_INITIAL_LOAD_OBJECTS_COUNT" ] ; then
          exit 0
        fi
      fi
    done
  SLEEPS=$((SLEEPS+1))
  sleep 1
done
exit 1