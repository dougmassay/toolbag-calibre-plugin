#!/bin/sh

# Create new translation strings messages.po file:

find . -type f -name "*.py" | xgettext --output=messages.pot -f -

# Merge (update) with existing template and finsished translations files

msgmerge -NU --backup=none ./translations/Trad.pot messages.pot
for i in ./translations/*.po; do
    [ -f "$i" ] || break
    msgmerge -NU --backup=none "$i" messages.pot
done
#msgmerge -NU ./translations/fr.po messages.pot
#msgmerge -NU ./translations/es.po messages.pot
msgfmt -o ./translations/fr.mo ./translations/fr.po
msgfmt -o ./translations/es.mo ./translations/es.po

rm ./messages.pot
