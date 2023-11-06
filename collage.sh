#!/bin/bash
#===============================================================================
#
#          FILE:  collage.sh
#
#         USAGE:  ./collage.sh
#
#   DESCRIPTION:
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:   (),
#       COMPANY:
#       VERSION:  1.0
#       CREATED:  06/11/23 16:53:46 CET
#      REVISION:  ---
#===============================================================================

for i in {1..50..1}
do
    ffmpeg -pattern_type glob -i "frames/*Cust$i.png" -filter_complex "scale=900:900,tile=4x1" frames/output$i.png
done

cp frames/output1.png frames/output.png

ffmpeg -i frames/output%d.png -frames 49 -loop 2 frames/output.gif
