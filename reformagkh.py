"""
Этот клас предоставляет доступ к сайту реформа жкх


"""

import requests #
import json #
import getpass #

urls = {'login':'https://ais.reformagkh.ru/user/login',
'organizations':'https://ais.reformagkh.ru/d988/organizations/registry?page=1&start=0&limit=10000',
        'homes':'https://ais.reformagkh.ru/d988/mkd/mkd-disclosure?page=1&start=0&limit=10000',
        'services':'https://ais.reformagkh.ru/d988/mkd-profile/get-communal-services/$building_id$?page=1&start=0&limit=10000',
        'service':'https://ais.reformagkh.ru/d988/mkd-profile/communal-services/$building_id$'}

class Reformagkh:
	def __init__(self, username, **opts):
		if isinstance(username,(str)):
			if len(username.strip()) == 0:
				raise Exception("Имя пользователя не может быть пустым")
		else:
			raise Exception("Имя пользователя не является текстом")
		self.__username = username
		post_data = {'identity':username, 'credential': opts['passwd'] if 'passwd' in opts else getpass.getpass('Пароль: ')}
		self.__s = requests.Session()
		self.__s.headers.update({'X-Requested-With':'XMLHttpRequest', 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0', 'Host':'ais.reformagkh.ru'})
		try:
			response = self.__s.post(urls['login'], data = post_data)
		except requests.exceptions.ConnectionError as e:
			raise Exception("Произошла ошибка при подключении, проверте наличие интернете")
		except requests.exceptions.ConnectTimeout as e:
			raise Exception("Удаленный сервер не отвечает")
		except Exception as e:
			raise Exception("Необрабатываетмая ошибка при попытке входа на сайт https://ais.reformagkh.ru")
		try:
			jresponse = json.loads(response.text)
		except Exception as e:
			raise Exception("Неверный формат ответа с сетвера при попытке входа в систему")
		if jresponse["success"]:
			if 'msg' in jresponse:
				raise Exception(jresponse['msg'])
		else:
			raise Exception("Произошла ошибка при входе в систему", jresponse)

	def user(self):
		return self.__username

	def organizations(self):
		try:
			response = self.__s.get(urls['organizations'])
		except requests.exceptions.ConnectionError as e:
			raise Exception("Произошла ошибка при подключении, проверте наличие интернете")
		except requests.exceptions.ConnectTimeout as e:
			raise Exception("Удаленный сервер не отвечает")
		except Exception as e:
			raise Exception("Необрабатываетмая ошибка при попытке получения списка организаций")
		try:
			jresponse = json.loads(response.text)
		except Exception as e:
			raise Exception("Неверный формат ответа с сетвера при попытке получения списка организаций")
		if 'success' in jresponse:
			raise Exception(jresponse)
		else:
			return [{'id':x['id'], 'title': x['title'], 'admin': x['administrator']} for x in jresponse['data']]

	def homes(self):
		try:
			response = self.__s.get(urls['homes'])
		except requests.exceptions.ConnectionError as e:
			raise Exception("Произошла ошибка при подключении, проверте наличие интернете")
		except requests.exceptions.ConnectTimeout as e:
			raise Exception("Удаленный сервер не отвечает")
		except Exception as e:
			raise Exception("Необрабатываетмая ошибка при попытке получения списка домов")
		try:
			jresponse = json.loads(response.text)
		except Exception as e:
			raise Exception("Неверный формат ответа с сетвера при попытке получения списка домов", e)
		if 'success' in jresponse:
			raise Exception(jresponse)
		else:
			return [{'id':x['id'], 'org':x['organization'], 'orgid':x['organizationid'], 'address':x['fulladdress'], 'space':x['areatotal']} for x in jresponse['data']]


	def get_communal_services(self, building_id):
		try:
			response = self.__s.get(urls["services"].replace("$building_id$",str(building_id)))
		except requests.exceptions.ConnectionError as e:
			raise Exception("Произошла ошибка при подключении, проверте наличие интернете")
		except requests.exceptions.ConnectTimeout as e:
			raise Exception("Удаленный сервер не отвечает")
		except Exception as e:
			raise Exception("Необрабатываетмая ошибка при попытке получения списка коммунальных ресурсов")
		try:
			jresponse = json.loads(response.text)
		except Exception as e:
			raise Exception("Неверный формат ответа с сетвера при попытке получения списка коммунальных ресурсов", e)
		if jresponse['success']:
			return [{'house':x['house'],'id':x['id'],'id':x['id'],'type':x['textType'],'typeid':x['type'],'statusid':x['fillingFact'],'status':x['textFilling']} for x in jresponse['data']["data"]]
		else:
			raise Exception(jresponse)

	def communal_service_get(self,building_id, service):
		try:
			response = self.__s.get(urls["service"].replace("$building_id$",str(building_id)), params={'serviceId':str(service)})
		except requests.exceptions.ConnectionError as e:
			raise Exception("Произошла ошибка при подключении, проверте наличие интернете")
		except requests.exceptions.ConnectTimeout as e:
			raise Exception("Удаленный сервер не отвечает")
		except Exception as e:
			raise Exception("Необрабатываетмая ошибка при попытке получения списка коммунальных ресурсов")
		try:
			jresponse = json.loads(response.text)
		except Exception as e:
			raise Exception("Неверный формат ответа с сетвера при попытке получения списка коммунальных ресурсов", e)
		if jresponse['success']:
			ret = {}
			for i in jresponse['data']:
				if isinstance(i,(list)):
					ret[i[16:-1]] = []
					for j in jresponse['data'][i]:
						ret_in = {}
						for k in j:
							ret_in[i[16:-1]] = k
						ret[i[16:-1]].append(ret_in)
				else:
					ret[i[16:-1]] = jresponse['data'][i]
			return ret
		else:
			raise Exception(jresponse)

	def communal_service_set(self, building_id, data):
		r = lambda x: 'communalService[$]'.replace('$',x)
		ad = lambda i,n: '[$i][$n]'.replace('$i',str(i)).replace('$n',str(n))
		new_data = {}
		for i in data:
			if isinstance(data[i],(list)):
				for j in range(len(data[i])):
					for k in data[i][j]:
						new_data[(r(i)+ad(j,k))] = data[i][j][k]
			else:
				new_data[r(i)] = data[i]
		new_data['serviceId'] = data['id']
		try:
			response = self.__s.post(urls["service"].replace("$building_id$",str(building_id)), data = new_data)
		except requests.exceptions.ConnectionError as e:
			raise Exception("Произошла ошибка при подключении, проверте наличие интернете")
		except requests.exceptions.ConnectTimeout as e:
			raise Exception("Удаленный сервер не отвечает")
		except Exception as e:
			raise Exception("Необрабатываетмая ошибка при попытке получения списка коммунальных ресурсов")
		try:
			jresponse = json.loads(response.text)
		except Exception as e:
			raise Exception("Неверный формат ответа с сетвера при попытке получения списка коммунальных ресурсов", e)
		if jresponse['success']:
			return True
		else:
			raise Exception("Ошибка при обновлении данных по коммунальным услугам", jresponse)

	def communal_service_add_tariff(self,data,startedDate,unit, tariff):
		#houseCommunalServiceCosts
		data['houseCommunalServiceCosts'].append({'tariff':tariff,'tariffStartedDate':startedDate, 'unitOfMeasurement':unit})
		data['tariff'] = tariff
		data['tariffStartedDate'] = startedDate
		data['unitOfMeasurement'] = unit

	def communal_service_add_act(self,data,docDate, docNum, docOrg):
		#houseCommunalServiceNormativeActs
		data['houseCommunalServiceNormativeActs'].append({'documentNumber':docNum,'documentDate':docDate, 'documentOrgName':docOrg})
		data['documentNumber'] = docNum
		data['documentDate'] = docDate
		data['documentOrgName'] = docOrg



