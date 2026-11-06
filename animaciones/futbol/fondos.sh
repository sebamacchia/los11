#!/bin/bash
# Fondos desenfocados (con el logo UEFA nítido encima) y recortes para las ventanas de video (PiP).
set -e
V=../../proyectos/estambul-2005/material/fuentes/final_uefa.mp4
A=assets
fondo() { # nombre desde hasta factor_lentitud duracion
  ffmpeg -loglevel error -y -ss $2 -to $3 -i $V -an -filter_complex \
   "[0:v]setpts=$4*PTS,split[a][b];[a]gblur=sigma=22,eq=brightness=-0.16:saturation=0.55,vignette=PI/4[f];[b]crop=175:100:1665:30,eq=brightness=-0.16:saturation=0.55[l];[f][l]overlay=1665:30,trim=duration=$5,setpts=PTS-STARTPTS" \
   -r 30 -c:v libx264 -crf 20 -pix_fmt yuv420p $A/$1.mp4
}
corte() { # nombre desde hasta
  ffmpeg -loglevel error -y -ss $2 -to $3 -i $V -an -r 30 -c:v libx264 -crf 18 -pix_fmt yuv420p $A/$1.mp4
}
fondo rep_fondo 384.0 387.0 2.4 7
fondo pen_fondo 700.9 706.2 1.75 9
fondo rel_fondo 493.3 501.8 1.07 9
fondo ali_fondo 208.0 215.2 1.0 7
corte rep_pip_a 387.0 391.6
corte rep_pip_b 394.0 396.4
corte pen_pip 640.7 647.2
corte rl_maldini 273.6 274.7
corte rl_crespo 329.0 330.4
corte rl_gerrard 394.5 395.5
corte rl_smicer 424.0 425.0
corte rl_alonso 464.5 465.5
corte rl_dudek 498.6 501.8
