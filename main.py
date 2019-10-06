#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python version: 3.7.3

'''
author: Willian Nascimento
github: d4sein
license: The Unlicense
email: williann.nasc@gmail.com
'''

import os
from sys import argv
import sqlite3
import json
import re
import time

import colorama
import asyncio
import requests
from bs4 import BeautifulSoup

from argparser import parser, command
from format import fmt


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

conn = sqlite3.connect('data.db')
c = conn.cursor()


colorama.init()


class Database:
    '''Holds all methods that interact directly with the database'''
    def init(self, c: object) -> None:
        '''Tries to create a new table called `animes`

        Parameters:
            c: object
            Cursor object from the sqlite3 connection
        '''
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS animes (
                            title text,
                            description text,
                            id int,
                            latest int
                            )''')

        except sqlite3.OperationalError:
            pass

    async def add(self, title: str, soup: object) -> bool:
        '''Adds an Anime to the database
    
        Parameters:
            title: str
            The Anime's title

            soup: object
            The website where to scrape from
        '''
        anime_id = re.search('hs_showid = (\\d+)', soup.text).group(1)

        website = requests.get(config['prefix'] + anime_id)

        latest = re.search('id="(\\d+?)"', str(website.content)).group(1)
        latest = int(latest)

        try:
            description = soup.find_all('p')[1].text

        except Exception:
            description = None

        try:
            c.execute('INSERT INTO animes VALUES (:title, :description, :id, :latest)', (title, description, anime_id, latest))
        
        except sqlite3.OperationalError:
            return False

        else:
            conn.commit()
            return True

    async def remove(self, title: str) -> bool:
        '''Removes an Anime from the database

        Parameters:
            title: str
            The Anime's title
        '''
        try:
            c.execute('DELETE FROM animes WHERE title=:title', (title,))

        except sqlite3.OperationalError:
            return False

        else:
            conn.commit()
            return True

    async def update(self, latest: int, title: str) -> bool:
        '''Updates latest release from an Anime

        Parameters:
            latest: int
            The latest release

            title: str
            The Anime's title
        '''
        try:
            c.execute('UPDATE animes SET latest=:latest WHERE title=:title', (latest, title))
        
        except sqlite3.OperationalError:
            return False

        else:
            conn.commit()
            return True

    async def reset(self) -> bool:
        '''Resets the database'''
        try:
            c.execute('DROP TABLE animes')
        
        except sqlite3.OperationalError:
            return False

        else:
            conn.commit()
            return True

    async def backup(self) -> bool:
        '''Creates a backup file'''
        bkp_conn = sqlite3.connect('backup.db')
        bkp_c = bkp_conn.cursor()

        try:
            bkp_c.execute('''CREATE TABLE animes (
                            title text,
                            description text,
                            id int,
                            latest int
                            )''')

            bkp_c.execute('ATTACH DATABASE "data.db" AS data')
            bkp_c.execute('INSERT INTO animes SELECT * FROM data.animes')

        except sqlite3.OperationalError:
            return False

        else:
            bkp_conn.commit()
            bkp_conn.close()
            return True

    async def restore(self) -> bool:
        '''Restores a backup file'''
        try:
            c.execute('ATTACH DATABASE "backup.db" AS backup')
            c.execute('INSERT INTO animes SELECT * FROM backup.animes')

        except sqlite3.OperationalError:
            return False

        else:
            conn.commit()
            return True


db = Database()
db.init(c)


class Application:
    parser.config(default_message='Released or Not')

    # docstrings are used to set command's description

    @command.positional({'title': 'The Anime\'s title'})
    @command.name('follow')
    async def follow(self, title: str) -> None:
        '''Starts following an Anime'''
        try:
            website = requests.get(config['website'] + title)

        except Exception as e:
            print('Something went wrong:', e)
            
        if website.ok:
            soup = BeautifulSoup(website.content, 'html.parser')
            title = soup.select_one('title').text.split(' – ')[0]
            
            c.execute('SELECT * FROM animes WHERE title=:title', (title,))
    
            titles = [item[0] for item in c.fetchall()]

            if title in titles:
                print(f'You\'re already following "{title}".')

            else:
                confirmation = await db.add(title, soup)

                if confirmation:
                    print(f'"{fmt.bold + title + fmt.reset}" has been added to the database.')

                else:
                    print(f'Something went wrong, it was not possible to add "{fmt.bold + title + fmt.reset}" to the database.')

        else:
            print('Something went wrong, it was not possible to access the main source.')


    @command.positional({'title': 'The anime\' title'})
    @command.name('unfollow')
    async def unfollow(self, title: str) -> None:
        '''Stops following an Anime'''
        c.execute('SELECT * FROM animes WHERE title=:title', (title,))

        titles = [item[0] for item in c.fetchall()]

        if title in titles:
            confirmation = await db.remove(title)

            if confirmation:
                print(f'"{fmt.bold + title + fmt.reset}" has been removed from the database.')

            else:
                print(f'Something went wrong, it was not possible to remove "{fmt.bold + title + fmt.reset}" from the database.')

        else:
            print('You\'re not following this Anime.')


    @command.name('update')
    async def update(self) -> None:
        '''Checks if new episodes have been released'''
        new = False

        c.execute('SELECT * FROM animes')

        for anime in c.fetchall():
            title, description, anime_id, ep = anime

            try:
                website = requests.get(config['prefix'] + str(anime_id))

            except Exception:
                print(f'Something went wrong, it was not possible to check new releases for "{fmt.bold + title + fmt.reset}".')
                latest = ep

            else:
                latest = re.search('id="(\\d+?)"', str(website.content)).group(1)
                latest = int(latest)

            if ep < latest:
                new = True

                for release in range(ep, latest):
                    print(f'{fmt.bold}A new episode of "{title}" has been released! [{fmt.bronze}EP {(release + 1):02d}{fmt.reset + fmt.bold}]{fmt.reset}')

                    if config['download']['status']:
                        try:
                            torrent_page = BeautifulSoup(website.content, 'html.parser')
                            torrent_files = torrent_page.find(id=release).find_all(title='Torrent Link')

                        except Exception:
                            print(f'  {fmt.light_gray}Something went wrong, it was not possible to access the torrent page.{fmt.reset}')

                        else:
                            quality = config['download']['quality']

                            if quality == '480':
                                torrent = torrent_files[0]['href']

                            elif quality == '720':
                                torrent = torrent_files[1]['href']

                            else:
                                torrent = torrent_files[2]['href']

                            if not os.path.exists('./torrents'):
                                os.makedirs('./torrents')

                            try:
                                r = requests.get(torrent)

                                with open(f'./torrents/{title}-{release}.torrent', 'wb') as f:
                                    f.write(r.content)

                            except Exception:
                                print(f'  {fmt.light_gray}Something went wrong, it was not possible to download the torrent file for this episode.{fmt.reset}')

                            else:
                                print(f'  {fmt.light_gray}Torrent file for this episode has been downloaded.{fmt.reset}')

                confirmation = await db.update(latest, title)

                if not confirmation:
                    print(f'''Something went wrong, it was not possible to update latest episode for "{fmt.bold + title + fmt.reset}" in the database.
You may experience misleading release notifications for this Anime in the future.''')

        if not new:
            print('There are no new releases.')


    @command.name('list')
    async def list(self) -> None:
        '''Shows a list with all the Animes being followed'''
        c.execute('SELECT * FROM animes')
        
        for title, description, anime_id, ep in c.fetchall():
            print(f'{fmt.bold + title} [{fmt.bronze}EP {ep}{fmt.reset + fmt.bold}]')


    @command.positional({'title': 'The Anime\'s title'})
    @command.name('description')
    async def description(self, title: str) -> None:
        '''Returns the description of an Anime'''
        c.execute('SELECT * FROM animes WHERE title LIKE :title COLLATE NOCASE', (f'%{title}%',))
        title, description, anime_id, ep = c.fetchone()

        if description:
            print(fmt.bold + title + fmt.reset)
            print(description)

        else:
            print(f'There is no description for "{title}".')


    @command.positional({'title': 'The Anime\'s title'})
    @command.name('search')
    async def search(self, title: str) -> None:
        '''Searches for an Anime'''
        try:
            website = requests.get(config['search'] + title)

        except Exception:
            print('Something went wrong, it was not possible to make a search request.')
            return
        
        if website.ok:
            soup = BeautifulSoup(website.content, 'html.parser')
            titles = soup.find_all('h4')

        if not titles:
            print('There were no results for this title.')

        else:
            for title in titles:
                print(f'"{fmt.bold + title.text + fmt.reset}"')


    @command.keyword({'quality': 'The video quality (480, 720, 1080)'})
    @command.optional({'on': 'Sets download to active', 'off': 'Sets download to inactive'})
    @command.name('download')
    async def download(self, on: bool=False, off: bool=False, quality: str=None) -> None:
        '''Sets download status'''
        if not on and not off:
            return print('Download is active.' if config['download']['status'] else 'Download is inactive.')

        if on:
            config['download']['status'] = True

            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            print('Download has been set to active.')

        elif off:
            config['download']['status'] = False

            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            print('Download has been set to inactive.')

        if quality in ['480', '720', '1080']:
            config['download']['quality'] = quality

            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            print(f'Video quality has been set to {quality}p.')


    @command.keyword({'timer': 'Sets the interval (in minutes) in which the program will update. Defaults to 60 minutes.'})
    @command.name('auto')
    async def auto(self, timer: int=60) -> None:
        '''Runs the program in autopilot'''
        try:
            timer = int(timer)

        except TypeError:
            return print('Something went wrong while setting `timer`.')

        if timer < 15:
            return print('Parameter `timer` can\'t be set to less than 15 minutes.')

        print(f'''Timer has been set to {timer} minutes. Update starts after first cicle.
Ctrl + C to cancel autopilot.''')
    
        try:
            while True:
                time.sleep(timer * 60)
                await self.update()

        except KeyboardInterrupt:
            pass


    @command.name('reset')
    async def reset(self) -> None:
        '''Resets the database'''
        confirmation = await db.reset()

        if confirmation:
            print('The database has been reseted.')

        else:
            print('Something went wrong, it was not possible to reset the database.')


    @command.name('backup')
    async def backup(self) -> None:
        '''Creates a backup file for the database'''
        confirmation = await db.backup()

        if confirmation:
            print('The backup file has been created.')

        else:
            print('''Something went wrong, it was not possible to create the backup file.
Make sure there is no other backup file in the program directory.''')

    @command.name('restore')
    async def restore(self) -> None:
        '''Restores a backup file into the database'''
        confirmation = await db.restore()

        if confirmation:
            print('The backup file has been restored.')

        else:
            print('Something went wrong, it was not possible to restore the backup file.')


if __name__ == '__main__':
    asyncio.run(parser.run(Application))
    conn.close()
