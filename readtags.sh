#!/usr/bin/env bash
app="NewPipe"
cat .tags.ini | grep $app | sed "s/${app}:.*/${app}/"
