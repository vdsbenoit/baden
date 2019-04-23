Baden [![Build Status](https://travis-ci.org/vdsbenoit/baden.svg?branch=master)](https://travis-ci.org/vdsbenoit/baden)
=====
This software is designed to manage a game played by a huge amount of players IRL.
It was first designed for a boyscout game involving about 1000 players.

## Players distribution

- games are duel battles: one team vs another team
- victories give 2 points & evens 1 point
- each team plays every game
- team are shuffled to avoid playing several time against the same opponent
- team can be sorted by gender (only female duels & only male duels)

## Scores management

- each team and game has a dedicated QR code
- when a duel ends, QR codes are scanned and score is recorded
- players can check their scores through their QR codes
- game administrator haves access to a live score board

## Dev stack
Back-end:
- python
- MongoDB + MongoEngine
- CherryPy

Front-end:
- jQuery
- Bootstrap
- Nimiq QR scanner

Server:
- nginx
- Docker

Roadmaps creation:
- docxcompose
- docxtpl
- pyqrcode