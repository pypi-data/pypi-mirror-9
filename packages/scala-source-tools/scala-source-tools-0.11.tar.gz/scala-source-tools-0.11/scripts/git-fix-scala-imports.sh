#!/bin/sh

SINCE=HEAD^
if [ $# == 1 ]; then
  SINCE=$1
fi

cd "$(git rev-parse --show-toplevel)"
git show --pretty="format:" --name-only $SINCE | sort | uniq | grep scala$ | xargs scala_import_sorter.py