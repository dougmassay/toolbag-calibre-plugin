#!/bin/bash

# Create new translation strings messages.po file:

find . -type f -name "*.py" | xgettext --output=messages.pot --sort-by-file -f -

# Merge (update) with existing template and finsished translations files

msgmerge -NU --backup=none --sort-by-file ./translations/Trad.pot messages.pot
for i in ./translations/*.po; do
    [ -f "$i" ] || break
    echo "$i"
    msgmerge -NU --backup=none --sort-by-file "$i" messages.pot
    mo_name=${i::-3}
    echo "$mo_name"
    msgfmt -o "$mo_name.mo" "$i"
done

rm ./messages.pot
