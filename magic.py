import subprocess
import sys
import time
from datetime import datetime as datetime

try:
	import argparse
	import lxml
	from bs4 import BeautifulSoup as bs
	from selenium import webdriver
except Exception:
	subprocess.check_call([sys.executable, "-m", "pip", "install", 'Wheel'])
	subprocess.check_call([sys.executable, "-m", "pip", "install", 'argparse'])
	subprocess.check_call([sys.executable, "-m", "pip", "install", 'lxml'])
	subprocess.check_call([sys.executable, "-m", "pip", "install", 'beautifulsoup4'])
	subprocess.check_call([sys.executable, "-m", "pip", "install", 'selenium'])
	import argparse
	import lxml
	from bs4 import BeautifulSoup
	from selenium import webdriver

parser = argparse.ArgumentParser(description="This program parses a file for all Magic: The Gathering card names. It then looks up prices for each card on tcgplayer.com and writes to the same file.")
parser.add_argument("-f", "--file", default="cards.txt", help="Point to the absolute file address or to the file name in the same folder as this script. Note: If the file is in the same directory as this script, you can just say the name of the file.")
parser.add_argument("-c", "--card", help="Add the specific card name after this flag to look up that specific card. Note: If the card has spaces, wrap the whole card name in double quotes. IF THE CARD HAS A COMMA, REPLACE IT WITH A PERIOD. Cannot be combined with -f.")
parser.add_argument("-b", "--base", action="store_true", help="Looks for the card's/s' base card price.")
parser.add_argument("-bl", "--borderless", action="store_true", help="Looks for the card's/s' borderless card price.")
parser.add_argument("-pr", "--pre-release", action="store_true", help="Looks for the card's/s' pre-release card price.")
parser.add_argument("-p", "--promo", action="store_true", help="Looks for the specific card's/s' promo card price.")
parser.add_argument("-s", "--showcase", action="store_true", help="Looks for the specific card's/s' showcase card price.")
parser.add_argument("-e", "--extended-art", action="store_true", help="Looks for the specific card's/s' extended art card price.")
parser.add_argument("-a", "--all", action="store_true", help="Prints all prices for all variants.")
parser.add_argument("-fl", "--foil", action="store_true", help="Searches on for the foil variant (must use separately even if using -a)")
args = parser.parse_args()

def parse_all_args(args):
	all_args = [None, None, None, None, None, None, None, None, None, None]
	temp_args = str(args).replace("Namespace(", "").replace(")", "").split(',')

	for i in range(len(temp_args)):
		temp_args[i] = temp_args[i].strip()

	try:
		#File
		all_args[0] = (temp_args[0].split('\''))[1]
		#Card
		all_args[1] = (temp_args[1].split('='))[1].replace('\'', '').replace('.', ',')
		#Base
		all_args[2] = (temp_args[2].split('='))[1].replace('\'', '')
		#Borderless
		all_args[3] = (temp_args[3].split('='))[1].replace('\'', '')
		#Pre-release
		all_args[4] = (temp_args[4].split('='))[1].replace('\'', '')
		#Promo
		all_args[5] = (temp_args[5].split('='))[1].replace('\'', '')
		#Showcase
		all_args[6] = (temp_args[6].split('='))[1].replace('\'', '')
		#Extended Art
		all_args[7] = (temp_args[7].split('='))[1].replace('\'', '')
		#All
		all_args[8] = (temp_args[8].split('='))[1].replace('\'', '')
		#Foil
		all_args[9] = (temp_args[9].split('='))[1].replace('\'', '')
	except IndexError:
		return all_args

	return all_args

def bs_(soup):
	return bs(soup, features="lxml")

def retry_page(url, soup, driver):
	counter = 0

	while driver.current_url == "https://www.tcgplayer.com/uhoh":
		print("Bad page...")
		counter += 1

		driver.get(url)
		html = driver.page_source
		soup = bs_(html)
		soup = bs_(soup.prettify())

		if counter >= 5:
			print("Could not reach page.")
			return False
		elif len(soup.find_all(class_="martech-error-page")) == 0:
			print("Breaking...")
			break

	return True

def wait_for_page(url, driver):
	html = driver.page_source
	soup = bs_(html)
	soup = bs_(soup.prettify())

	while len(soup.find_all(class_="search-result")) == 0 or len(soup.find_all(class_="is-active marketplace-header__logo")) == 0:
		html = driver.page_source
		soup = bs_(html)
		soup = bs_(soup.prettify())

		if len(soup.find_all(class_="blank-slate__title")) > 0:
			print("No results :(  (check spelling of card?)")
			return False
		elif len(soup.find_all(class_="martech-error-page")) > 0:
			return retry_page(url, soup, driver)
	return True

def find_card(driver, url, card_name):
	#0 = Name
	#1 = Card pack
	#2 = Card rarity
	#3 = Card number
	#4 = "As low as"
	#5 = Number of listings
	#6 = Market price
	card_info = [None, None, None, None, None, None, None]
	card_list = []

	driver.get(url)

	cont = wait_for_page(url, driver)

	html = driver.page_source
	soup = bs_(html)
	soup = bs_(soup.prettify())

	try:
		if cont:
			for i in soup.find_all(class_="search-result"):
				if card_name in str(i.find_all(class_="search-result__title")).split('\n')[1].strip()[0:len(card_name)]:
					card_info[0] = str(i.find_all(class_="search-result__title")).split('\n')[1].strip()
					card_info[1] = str(i.find_all(class_="search-result__subtitle")).split('\n')[1].strip()
					card_info[2] = str(i.find_all(class_="search-result__rarity")).split('\n')[2].strip()
					try:
						card_info[3] = str(i.find_all(class_="search-result__rarity")).split('\n')[8].strip()
					except IndexError:
						card_info[3] = ""

					if len(soup.find_all(class_="notification notification--out-of-stock inventory")) != 0:
						card_info[4] = "Out of stock"
						card_info[5] = "No listings"
						card_info[6] = "Out of stock"
					else:
						if len(i.find_all(class_="inventory__price-with-shipping")) != 0:
							card_info[4] = str(i.find_all(class_="inventory__price-with-shipping")).split('\n')[1].strip()
							card_info[5] = str(i.find_all(class_="inventory__listing-count inventory__listing-count-block")).split('\n')[2].strip().split(' ')[0]
						else:
							card_info[4] = "Out of stock"
							card_info[5] = "No listings"

						if len(i.find_all(class_="search-result__market-price search-result__market-price--unavailable")) != 0:
							card_info[6] = "No price available"
						else:
							card_info[6] = str(i.find_all(class_="search-result__market-price--value")).split('\n')[1].strip()

					card_list.append(card_info)
					card_info = [None, None, None, None, None, None, None]
	except IndexError:
		print(i)
		for x in range(len(card_info)):
			print(card_info[x])
		card_info = [None, None, None, None, None, None, None]
		print("Grabbed none :(  (contact me if you see this)")

	if len(soup.find_all(class_="pagination-button")) != 0 and len(soup.find_all(class_="pagination-button")) != int(url[-1]):
		c_page = url[-1]
		n_page = int(url[-1]) + 1
		temp = find_card(driver, url.replace(c_page, str(n_page)), card_name)
		for i in range(len(temp)):
			card_list.append(temp[i])

	return card_list

def url_create(card):
	return 'https://www.tcgplayer.com/search/magic/product?productLineName=magic&q=' + card.replace(' ', '+') + '&view=grid&ProductTypeName=Cards&page=1'

def read_file(file):
	f = open(file, "r")
	cards = f.readlines()
	f.close()
	return cards

def check_duplicate(cards_gone_through, card_name):
	for i in range(len(cards_gone_through)):
		if cards_gone_through[i] == card_name:
			print("Duplicate found:", (card_name + "..."))
			return True
	return False

driver = webdriver.Firefox()

args = parse_all_args(args)

cards = []
filename = args[0]

if args[1] != "None":
	cards.append(str(args[1]))
else:
	cards = read_file(filename)

all_card = []
card_names = []

start_time = datetime.now()
print(start_time.strftime("%H:%M:%S"))

for i in range(len(cards)):
	cards[i] = str(cards[i]).replace("\n", "")
	check = check_duplicate(card_names, cards[i])
	if check == False:
		print("Searching for", (cards[i] + "..."))
		all_card.append(find_card(driver, url_create(cards[i]), cards[i]))
		card_names.append(cards[i])

driver.close()

full_line = ""

print("Writing to file...")


num_cards = 0

try:
	f = open(str(datetime.now().strftime("%m-%d-%y")) + " card values.xls", "a")
	f.write("Name\tPack\tRarity\tNumber\tMin\tNum listings\tMarket price\n")

	for i in range(len(all_card)):
		for x in range(len(all_card[i])):
			for j in range(len(all_card[i][x])):
				full_line += (str(all_card[i][x][j]) + "\t")
			f.write(full_line.strip() + "\n")
			full_line = ""
			num_cards += 1
	f.close()
except PermissionError:
	print("The export file is currently opened. Please copy/paste the following:")
	for i in range(len(all_card)):
		for x in range(len(all_card[i])):
			for j in range(len(all_card[i][x])):
				full_line += (str(all_card[i][x][j]) + "\t")
			print(full_line.strip() + "\n")
			full_line = ""
			num_cards += 1

end_time = datetime.now()
print("\nFinished:", end_time.strftime("%H:%M:%S"))
print("Total number of cards:", num_cards)
print("Total time amounted:", (end_time - start_time))
print("Average card per minute:", "~" + (((str((end_time - start_time) / len(card_names)).split(':')))[2].split('.'))[0])