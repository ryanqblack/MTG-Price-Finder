# MTG-Price-Finder
This project is written in Python. It requires internet access to query https://www.tcgplayer.com. Certain flags/options have not been fully implemented yet. It will produce a .xls file containing the following about the given card(s):
 - Name
 - Pack
 - Rarity
 - Number
 - Minimum price listed
 - Number of listings
 - Market price

# Setup
You will need the latest version of Python. The default browser is Mozilla Firefox. You will need to download "geckodriver" and add that to your PATH.

You will need the following Python libraries:
 - argparse
 - lxml
 - beautifulsoup4
 - selenium

magic.py should install these, but will not make them globally available for all future Python scripts. All of these libraries can be installed using "pip" + the names used above.

Internet access is required.

Make a .txt file with all of the card names you want to look for. Use the "-f" option to point to the .txt file with all your cards.

# What's next?
 - Fully implement flags/options/optional arguments
 - Grab pictures from the website as well (as a flag; default "false")
