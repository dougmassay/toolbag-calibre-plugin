#!/bin/bash

# Create new translation strings messages.po file:

find . -type f -name "*.py" | xgettext --output=messages.pot -F -

# Merge (update) with existing template and finsished translations files

msgmerge -NU --backup=none ./translations/Trad.pot messages.pot
for i in ./translations/*.po; do
    [ -f "$i" ] || break
    echo "$i"
    msgmerge -NU --backup=none "$i" messages.pot
    mo_name=${i::-3}
    echo "$mo_name"
    msgfmt -o "$mo_name.mo" "$i"
done

rm ./messages.pot
