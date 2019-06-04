import requests
import json

with open('data.json', 'r') as f:
	data = json.load(f)

kimetsu_id = str(data['kimetsu'])
kimetsu = requests.head(f'https://www.dreamanimes.com.br/online/legendado/kimetsu-no-yaiba/episodio/{kimetsu_id}')

opm_id = str(data['opm'])
if int(opm_id) < 10:
	opm = requests.head(f'https://myanimesonline.net/episodios/one-punch-man-2-episodio-0{opm_id}/')
else:
	opm = requests.head(f'https://myanimesonline.net/episodios/one-punch-man-2-episodio-{opm_id}/')

dororo_id = str(data['dororo'])
dororo = requests.head(f'https://ww4.animesonline.online/video/dororo-episodio-{dororo_id}/')


if kimetsu.status_code == 200:
	print(f'Saiu ep novo de Kimetsu no Yaiba! EP {kimetsu_id}.')
	data['kimetsu'] += 1

	with open('data.json', 'w') as f:
		json.dump(data, f, sort_keys=False, indent=4)
else:
    print('Ainda não saiu ep novo de Kimetsu no Yaiba.') 


if opm.status_code == 200:
	print(f'Saiu ep novo de One Punch Man! EP {opm_id}.')
	data['opm'] += 1

	with open('data.json', 'w') as f:
		json.dump(data, f, sort_keys=False, indent=4)
else:
	print('Ainda não saiu ep novo de One Punch Man.')


if dororo.status_code == 200:
	print(f'Saiu ep novo de Dororo! EP {dororo_id}.')
	data['dororo'] += 1

	with open('data.json', 'w') as f:
		json.dump(data, f, sort_keys=False, indent=4)
else:
	print('Ainda não saiu ep novo de Dororo.')
