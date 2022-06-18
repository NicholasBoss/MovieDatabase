# Overview

This project was to create a catalog of movies to act like 'Blockbuster' or 'Redbox'. This program allows a user to enter movie data into the system and be able to update the amount of movies they have in their store. The program alerts the user if they run out of a movie and lets them know when that movie has been restocked.


[Software Demo Video](https://youtu.be/gTsaDKS9TTw)

# Cloud Database

Google Firestore



The structure of the database is as follows: I have my overall collection named 'movies' and each document within my collection is a movie. Within each movie I have the year, rating, studio, media type and quantity stored. Each movie also contains a list of actors, genres and special features.

# Development Environment

Python


Visual Studio Code

# Useful Websites

* [Google Firebase](https://console.firebase.google.com/)
* [Firestore Documentation](https://firebase.google.com/docs/firestore)

# Future Work

* Update to allow functionality of inserting more information into my lists
* Fix 'Popular' field in each document
* Ablilty to delete a whole document