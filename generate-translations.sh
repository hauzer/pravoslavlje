#!/usr/bin/env sh

pot=messages.pot
dir=translations
sr_latn_rs_po=translations/sr_Latn_RS/LC_MESSAGES/messages.po

pybabel extract -F babel.cfg -o ${pot} ./
pybabel init -l sr_Latn_RS -d ${dir} -i $pot
msgen -i ${pot} -o ${sr_latn_rs_po}
msgfilter -o ${sr_latn_rs_po} recode-sr-latin < ${sr_latn_rs_po}
pybabel compile -f -d ${dir}
