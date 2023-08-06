

#import requests
import urllib
import json

from .exceptions import CilenisApiException, CilenisValidationException

class Cilenis(object):

	protocol   = "http"
	host       = "api.cilenisapi.com/"
	apiurl     = "%s://%s" % (protocol,host)

	endpoints = {
		u"get_language_identifier" : u"language_identifier",
		u"get_sentiment"           : u"sentiment_analyzer",
		u"get_keywords"            : u"keyword_extractor",
		u"get_multiwords"          : u"multiword_extractor",
		u"get_entities"            : u"named_entity_recognizer",
		u"get_people"              : u"named_entity_recognizer",
		u"get_organizations"       : u"named_entity_recognizer",
		u"get_places"              : u"named_entity_recognizer",
		u"split"                   : u"tokenizer",
		u"get_keyword_context"     : u"concordancer",
		u"conjugate"               : u"conjugator",
		u"is_infinitive"           : u"conjugator",
		u"get_text_from_web"       : u"web_text_extractor",

		u"raw_endpoint"            : u"",
	}
	
	x_ratelimit_remaining  = None
	x_ratelimit = None

	def __init__(self, app_id=None, app_key=None, method="GET"):
		if not app_id or not app_key:
			raise CilenisValidationException(msg=u"app_id and app_key are mandatory", help=u"ex.: cilenisApi = Cilenis('app_id','app_key')")
		self.app_id  = app_id
		self.app_key = app_key



	def dotherealstaff(
			endpoint_name,
			lang_required=False,
			keyword_required=False,
			just_url=False,
			textandurl_notrequired=False):
		def wrap(f):
			def wrapped_f(self, *args, **kwargs):
				# Get args:
				text         = kwargs.get("text", None)
				url          = kwargs.get("url", None)
				lang         = kwargs.get("lang", None)
				keyword      = kwargs.get("keyword", None)
				raw_endpoint = kwargs.get("endpoint", None)
				raw_params   = kwargs.get("params", None)
				# Validate args:
				if just_url and not url:
					raise CilenisValidationException(msg=u"url is required", help=u"ex.: api.%s(url='http://google.es')" % (endpoint_name))
				if not textandurl_notrequired and not text and not url:
					raise CilenisValidationException(msg=u"text or url is required", help=u"ex.: api.%s(text='hola') or api.%s(url='http://google.es')" % (endpoint_name,endpoint_name))
				if keyword_required and not keyword:
					raise CilenisValidationException(msg=u"keyword is required", help=u"ex.: api.%s(keyword='helo', text='...') or api.%s(keyword='helo', url='http://google.es')" % (endpoint_name,endpoint_name))
				# Format request params:
				incoming = { "type":"text", "text":text } if text and not just_url else { "type":"url", "url":url }
				endpoint = self.endpoints[endpoint_name]
				url = "%s%s" % (self.apiurl,endpoint)
				params = {
					incoming["type"]: incoming[incoming["type"]],
					"format": "json",
					"app_id": self.app_id,
					"app_key": self.app_key
				}
				if lang_required:
					if not lang:
						if text: lang = self.get_language_identifier(text=text)
						else: lang = self.get_language_identifier(url=url)
					params["lang_input"] = lang
				if keyword_required: params["keyword"] = lang
				# RAW endpoint format params:
				if raw_endpoint and raw_params:
					endpoint = raw_endpoint
					url = "%s%s" % (self.apiurl,endpoint)
					params = raw_params

				# Call API:
				#response = requests.get( url=url, params=params )
				#kwargs['result_json'] = response.json()
				try:
					response = urllib.urlopen("%s?%s" % (url, urllib.urlencode(dict([k.encode('utf-8'),unicode(v).encode('utf-8')] for k,v in params.items())))).read()
					if raw_endpoint and raw_params: kwargs['response'] = response # response to raw_endpoint method
					else: kwargs['result_json'] = json.loads(response) # response added to main method (all others)
				except Exception, e: raise CilenisApiException(msg=unicode(e))

				return f(self, *args, **kwargs)
			return wrapped_f
		return wrap

	@dotherealstaff("get_language_identifier")
	def get_language_identifier(self, text=None, url=None, result_json=None):
		return result_json['lang']

	@dotherealstaff("get_sentiment", lang_required=True)
	def get_sentiment(self, text=None, url=None, lang=None, result_json=None):
		return result_json['polarity']['polarity_name'], result_json['polarity']['polarity_weight']

	@dotherealstaff("get_keywords", lang_required=True)
	def get_keywords(self, text=None, url=None, lang=None, result_json=None):
		return result_json['keyword_extractor']['keywords'], result_json['keyword_extractor']['text']

	@dotherealstaff("get_multiwords", lang_required=True)
	def get_multiwords(self, text=None, url=None, lang=None, result_json=None):
		return result_json['multiword_terms']

	@dotherealstaff("get_entities", lang_required=True)
	def get_entities(self, text=None, url=None, lang=None, entity="all", result_json=None):
		entities = result_json['entityextractor']['entities']
		html     = result_json['entityextractor']['text']
		if entity == "people":
			return [en for en in entities if en['tag'] == "PERS"]
		elif entity == "organizations":
			return [en for en in entities if en['tag'] == "ORG"]
		elif entity == "places":
			return [en for en in entities if en['tag'] == "LOCAL"]
		else:
			return entities, html
	def get_people(self, text=None, url=None, lang=None, entity="all", result_json=None):
		return self.get_entities(text=text,url=url,lang=lang,entity="people")
	def get_organizations(self, text=None, url=None, lang=None, entity="all", result_json=None):
		return self.get_entities(text=text,url=url,lang=lang,entity="organizations")
	def get_places(self, text=None, url=None, lang=None, entity="all", result_json=None):
		return self.get_entities(text=text,url=url,lang=lang,entity="places")

	@dotherealstaff("split", lang_required=True)
	def split(self, text=None, url=None, lang=None, result_json=None):
		return result_json['tokens']

	@dotherealstaff("get_keyword_context", lang_required=True, keyword_required=True, just_url=True)
	def get_keyword_context(self, keyword=None, text=None, url=None, lang=None, result_json=None):
		return result_json['ocurrences']

	@dotherealstaff("conjugate", lang_required=True)
	def conjugate(self, text=None, url=None, lang=None, result_json=None):
		if result_json['known'] <= 0 and result_json['conjugations'][0]['conjugation'][0]['tense'] == None:
			raise CilenisApiException(msg=unicode(result_json['conjugations'][0]['conjugation'][0]['code_tense']))
		return result_json['conjugations'], result_json['lang']

	@dotherealstaff("is_infinitive", lang_required=True)
	def is_infinitive(self, text=None, url=None, lang=None, result_json=None):
		return result_json['known'] >= 1

	@dotherealstaff("get_text_from_web", lang_required=True, just_url=True)
	def get_text_from_web(self, url=None, lang=None, result_json=None):
		return result_json['extractedText']

	@dotherealstaff("raw_endpoint", textandurl_notrequired=True)
	def raw_endpoint(self, endpoint=None, params=None, response=None):
		return response
















