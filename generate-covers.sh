#!/usr/bin/env sh

for pdf in static/pdfs/*; do
  cover_base="static/covers/$(basename ${pdf%.*})"
  cover_large="${cover_base}-large.png"
  convert -density 200 "${pdf}[0]" -background white -flatten -alpha off -resize x1200 "png24:${cover_large}"
  convert "${cover_large}" -resize 500x "png24:${cover_base}-medium.png"
  convert "${cover_large}" -resize 250x "png24:${cover_base}-small.png"
done
