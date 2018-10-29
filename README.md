# Timealyzer
This project allows you to find out how much time you've spent at specific locations

## Compatibility
Only works on Linux for me since my location history is quite large (~250mb json file) which adds up to around 2gb of RAM usage when loaded in Python.
On Windows even 64bit Python trows a memory error at me because of that but on linux it works.

## How to use
* Export your location history via [Google Takeout](https://takeout.google.com/settings/takeout)
* Locate the location history file and move it to the project folder
* Copy `config.ini.example` as `config.ini`
* Edit the example cathedral section with your own name for a location and change the address **or** latitude and longitude to your location
* _Optional: change radius parameter for smaller or bigger zone radius around point_
* Optional: Create a virtual environmnent if you want to create a more isolated dependancy installation
* Install the dependancies via `pip install -r requirements.txt`
* Run the script and tell it to load the history for the first time `python time_spent_checker.py -l <name of location history file including .json>`
* Wait for it to iterate over history _(takes some time for larger location histories)_
* Time spent is printed to the console
* _Optional: Next time use it without -l parameter to use cached version of location history for faster execution (except location history has changed)_

# Inspiration
Since I wanted to try some Data Science I gathered data by exporting most of my google data with google takeout including my location history.
I then thought about finding out how many hours of billard I've played since I started playing it a few months back and this is how this project was born.
