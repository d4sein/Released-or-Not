from argila import *
from bs4 import BeautifulSoup
import colorama
import requests
import time
import json
import re

try:
	colorama.init()
except Exception:
	pass

with open('data.json', 'r') as f:
	data = json.load(f)


class Commands(Argila):
	def __init__(self):
		super().__init__(Commands)

	@root
	def _root():
		return {
		'head': '\nScript that uses web scraping to track Anime releases',
		'version': 'Version 0.1.0',
		'greeting': 'Welcome!',
		'call': 'main.py',
		}

	@set_optional_params(['anime'])
	def add(anime) -> 'add':
		'''Adds an Anime to the list'''
		if not anime:
			anime = input('name: ')

		sufix = anime.replace(' ', '-').lower()

		try:
			site = requests.get(data['site'] + sufix)
			
			if site.ok:
				soup = BeautifulSoup(site.content, 'html.parser')
				title = soup.select_one('title').text.split(' – ')[0]
				
				if title in data['animes']:
					print('You\'re already following this Anime, bop.')
				else:
					Commands._add_to_data(title, soup)

			else:
				print('An error has occurred, bip bop.')
		except Exception:
			print('An error has occurred, bip bop.')


	def delete() -> 'del':
		'''Deletes an Anime from the list'''
		anime = input('name: ')

		try:
			if anime in data['animes']:
				data['animes'].pop(anime)
				print('Done!')
			else:
				print('You\'re not following this Anime.')
				exit()
		except Exception:
			print('An error has occurred, bip bop.')
			exit()

		with open('data.json', 'w') as f:
			json.dump(data, f, sort_keys=False, indent=4)
			f.close()

	def update() -> 'update':
		'''Checks if new episodes have been released'''
		new = False

		for title in data['animes']:
			animeID = data['animes'][title][0]
			current_release = data['animes'][title][1]
			synopsis = data['animes'][title][2]

			try:
				download_page = requests.get(data['prefix'] + animeID)
				latest_release = re.search('id="(\d+?)"', str(download_page.content)).group(1)
				latest_release = int(latest_release)
			except Exception:
				print('An error has occurred, bip bop.')

			if current_release < latest_release:
				new = True

				for i in range(current_release, latest_release):
					print(f'A new episode of {title} has been released! [\u001b[38;5;3mEP {i + 1}\u001b[0m]')

				kv = {
					title: [
						animeID,
						latest_release,
						synopsis
					]
				}
				
				data['animes'].update(kv)

				with open('data.json', 'w') as f:
					json.dump(data, f, sort_keys=False, indent=4)
					f.close()

		if new == False:
			print('There are no new releases. bip.')

	def list() -> 'list':
		'''Shows list of Animes being followed'''
		for title in data['animes']:
			ep = data['animes'][title][1]
			print(f'{title} [\u001b[38;5;3mEP {ep}\u001b[0m]')

	def erase() -> 'erase':
		'''Erases the list completely'''
		try:
			validation = input('Are you sure you want to erase your list? After that, you won\'t be able to recover it. [\u001b[38;5;3my\u001b[0m/\u001b[38;5;3mn\u001b[0m]\n')
		except Exception:
			pass

		if validation == 'y':
			data['animes'] = {}

			with open('data.json', 'w') as f:
				json.dump(data, f, sort_keys=False, indent=4)
				f.close()

			print('Done!')
		else:
			exit()

	def synopsis() -> 'synopsis':
		'''Shows an Anime synopsis'''
		anime = input('name: ')

		if anime in data['animes']:
			if data['animes'][anime][2] != 'empty':
				print(data['animes'][anime][2])
			else:
				print('There\'s no synopsis for this Anime. bop.')
		else:
			print('You\'re not following this Anime to see its synopsis. bip.')

	def backup() -> 'backup':
		'''Creates a backup.txt file'''
		backup = open('backup.txt','w+')

		for title in data['animes']:
			backup.write(f'{title}\n')

	def restore() -> 'restore':
		'''Restores list from a backup.txt file'''
		backup = open('backup.txt', 'r+')

		data = [line.strip() for line in backup]
		for title in data:
			Commands.add(title)

	def search() -> 'Search':
		'''Searches for an Anime'''
		anime = input('name: ')

		try:
			site = requests.get(data['search'] + anime)
			
			if site.ok:
				soup = BeautifulSoup(site.content, 'html.parser')
				titles = soup.find_all('h4')
		except Exception:
			print('An error has occurred, bip bop.')
			exit()

		if titles == []:
			print('I couldn\'t find anything, sorry. bip.')
		else:
			print()
			for title in titles:
				print(title.text)

	@set_help({'timer': 'Sets the interval between updates in minutes'})
	@set_optional_params(['timer'])
	def autopilot(timer) -> 'Autopilot':
		'''Runs the script in autopilot'''
		if timer == None:
			timer = 60

		try:
			timer = int(timer)
		except Exception:
			print('An error has occurred, bip bop.')
			exit()

		if timer < 15:
			print('You can\'t set the timer to less than 15 minutes.')
			exit()

		while True:
			Commands.update()
			time.sleep(timer * 60)

	def _add_to_data(title, soup):
		animeID = re.search('hs_showid = (\d+)', soup.text).group(1)
		download_page = requests.get(data['prefix'] + animeID)

		latest_release = re.search('id="(\d+?)"', str(download_page.content)).group(1)
		latest_release = int(latest_release)

		try:
			synopsis = soup.find_all('p')[1].text
		except Exception:
			synopsis = 'empty'

		kv = {
			title: [
				animeID,
				latest_release,
				synopsis
			]
		}

		data['animes'].update(kv)

		with open('data.json', 'w') as f:
			json.dump(data, f, sort_keys=False, indent=4)
			f.close()

		print('Done!')

if __name__ == '__main__':
	try:
		Commands()
	except KeyboardInterrupt:
		pass
