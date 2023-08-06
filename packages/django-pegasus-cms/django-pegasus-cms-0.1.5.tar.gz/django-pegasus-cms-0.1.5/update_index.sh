#!/usr/bin/env bash

. ~/.profile

LAST_INDEXED="`cat .last_indexed`"

set -e
if [ -n "$LAST_INDEXED" ]; then
    python manage.py update_index --remove --start="$LAST_INDEXED"
else
    python manage.py update_index --remove
fi

# update last-indexed
python -c "from django.utils import timezone; print '%s' % timezone.now()" > .last_indexed
