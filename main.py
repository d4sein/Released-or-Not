from parse import *
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


class Commands(Parse):
	def __init__(self):
		super().__init__(Commands)


	@set_root
	def _root():
		return {
		'application': 'ron',
		'version': 'Version 1.0.0',
		'greeting': 'Welcome!',
		'head': '''Released or Not v1.0.0
Willian Nascimento \u001b[38;5;3m<williann.nasc@gmail.com>\u001b[0m
Script that uses web scraping to track anime releases'''
		}


	def add():
		'''Adds a new Anime to your list'''
		name = input('name: ')
		
		if name in data['animes']:
			print('You\'re already following this Anime.')
			exit()

		url_name = name.replace(' ', '-').lower()

		try:
			site = requests.get(data['site'] + url_name)

			if site.ok:
				_add_to_data(name, site)
			else:
				print('Invalid.')
				exit()
		except Exception as e:
			print('An error occurred, bip bop.')
			exit()


	def remove():
		'''Removes an Anime from your list'''
		name = input('name: ')

		try:
			if name in data['animes']:
				data['animes'].pop(name)
				print('Done!')
			else:
				print('This Anime is not in your list.')
				exit()
		except Exception:
			print('An error occurred, bip bop.')
			exit()

		with open('data.json', 'w') as f:
			json.dump(data, f, sort_keys=False, indent=4)
			f.close()


	def update():
		'''Checks if a new episode has been released'''
		new = False

		for anime in data['animes']:
			anime_id = data['animes'][anime][0]

			try:
				download_page = requests.get(data['prefix'] + anime_id)
				latest_release = re.search('id="(\d+?)"', str(download_page.content)).group(1)
			except Exception as e:
				print('An error occurred, bip bop:', e)

			if data['animes'][anime][1] < int(latest_release):
				new = True

				print(f'A new episode of {anime} has been released! EP {int(latest_release)}.')

				data['animes'][anime] = [anime_id, int(latest_release)]

				with open('data.json', 'w') as f:
					json.dump(data, f, sort_keys=False, indent=4)
					f.close()

		if new == False:
			print('There are no new releases. Unlucky.')


	def list():
		'''Shows full list of Animes being followed'''
		for anime in data['animes']:
			ep = data['animes'][anime][1]
			print(f'\u001b[38;5;3m>\u001b[0m {anime} [\u001b[38;5;3mEP {ep}\u001b[0m]')


	def erase():
		'''Erases your list completely (no recovery)'''
		try:
			validation = input('Are you sure you want to erase your list? After that, you won\'t be able to recover it. [\u001b[38;5;3my\u001b[0m/\u001b[38;5;3mn\u001b[0m]\n>')
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


def _add_to_data(name, site):
	anime_id = re.findall('hs_showid = \d+', str(site.content))[0].replace(' ', '').split('=')[1]

	download_page = requests.get(data['prefix'] + anime_id)
	latest_release = re.search('id="(\d+?)"', str(download_page.content)).group(1)
	
	data['animes'][name] = [anime_id, int(latest_release)]
	with open('data.json', 'w') as f:
		json.dump(data, f, sort_keys=False, indent=4)
		f.close()

	print('Done!')



if __name__ == '__main__':
	Commands()
