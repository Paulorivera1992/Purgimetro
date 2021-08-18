#!/bin/sh
#
# This script will be executed *after* all the other init scripts.
# You can put your own initialization stuff in here if you don't
# want to do the full Sys V style init stuff.

# Ejecutar el script de demo en cada arranque:
sudo nohup python3 sensor_temp.py > output.txt &
sudo nohup python3 subir_dropbox.py > output.txt &

