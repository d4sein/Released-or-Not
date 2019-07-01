from argila import *
from bs4 import BeautifulSoup
import colorama
import requests
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
		'head': 'Script that uses web scraping to track anime releases',
		'version': 'Version 0.1.0',
		'greeting': 'Welcome!',
		'call': 'main.py',
		}

	def add() -> 'add':
		'''Adds an Anime to the list'''
		anime = input('name: ')

		sufix = anime.replace(' ', '-').lower()

		try:
			site = requests.get(data['site'] + sufix)
		except Exception:
			print('An error has occurred, bip bop.')
			exit()

		if site.ok:
			soup = BeautifulSoup(site.content, 'html.parser')
			title = soup.select_one('title').text.split(' – ')[0]
		else:
			print('Invalid anime title or couldn\'t be found.')
			exit()

		if title in data['animes']:
			print('You\'re already following this anime, bop.')
			exit()
		else:
			_add_to_data(title, site)

	def remove() -> 'remove':
		'''Removes an Anime from the list'''
		anime = input('name: ')

		try:
			if anime in data['animes']:
				data['animes'].pop(anime)
				print('Done!')
			else:
				print('You\'re not following this anime.')
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

			try:
				download_page = requests.get(data['prefix'] + animeID)
				latest_release = re.search('id="(\d+?)"', str(download_page.content)).group(1)
			except Exception:
				print('An error has occurred, bip bop.')

			if data['animes'][title][1] < int(latest_release):
				print(f'A new episode of {title} has been released! EP {int(latest_release)}.')

				kv = {
					title: [
						animeID,
						int(latest_release)
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
			print(f'\u001b[38;5;3m>\u001b[0m {title} [\u001b[38;5;3mEP {ep}\u001b[0m]')

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

def _add_to_data(title, site):
	animeID = re.search('hs_showid = (\d+)', str(site.content)).group(1)
	download_page = requests.get(data['prefix'] + animeID)
	latest_release = re.search('id="(\d+?)"', str(download_page.content)).group(1)
	
	kv = {
		title: [
			animeID,
			int(latest_release)
		]
	}

	data['animes'].update(kv)

	with open('data.json', 'w') as f:
		json.dump(data, f, sort_keys=False, indent=4)
		f.close()

	print('Done!')

if __name__ == '__main__':
	sys.argv = ['main.py', '-e']
	Commands()
