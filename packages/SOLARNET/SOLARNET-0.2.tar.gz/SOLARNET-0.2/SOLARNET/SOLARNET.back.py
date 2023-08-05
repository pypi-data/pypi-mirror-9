import os
import copy
from datetime import datetime
import dateutil.parser
import urllib, urlparse
import StringIO
import slumber

API = slumber.API("http://benjmam-pc:8000", auth = None)


class Time:
	def __init__(self, *args, **kwargs):
		
		attrs = ["year", "month", "day", "hour", "minute", "second"]
		# First case, we get a string
		if len(args) == 1 and isinstance(args[0], basestring):
			time = Time.from_string(args[0])
			for attr in attrs:
				setattr(self, attr, getattr(time, attr)) 
		# Second case we get value for the fields indenpendently
		else:
			for attr, arg in zip(attrs, args):
				if arg is None:
					setattr(self, attr, None)
				elif isinstance(arg, int) or (attr == "second" and isinstance(arg, float)):
					setattr(self, attr, arg)
				else:
					raise TypeError("Wrong type of argument for attribute %s" % attr)
			
			for attr, arg in kwargs.iteritems():
				if hasattr(self, attr):
					raise ValueError("Duplicate value for attribute %s" % attr)
				elif arg is None:
					setattr(self, attr, None)
				elif isinstance(arg, int) or (attr == "second" and isinstance(arg, float)):
					setattr(self, attr, arg)
				else:
					raise TypeError("Wrong type of argument for attribute %s" % attr)
		
		# Set remaining attributes to None
		for attr in attrs:
			if not hasattr(self, attr):
				setattr(self, attr, None)
		
		# Make some verifications
		if self.year is not None and self.year <= 0:
			raise ValueError("Wrong value %s for attribute year" % self.year)
		if self.month is not None and not 1 <= self.month <= 12:
			raise ValueError("Wrong value %s for attribute month" % self.month)
		if self.day is not None and not 1 <= self.day <= 31:
			raise ValueError("Wrong value %s for attribute day" % self.day)
		if self.hour is not None and not 0 <= self.hour <= 23:
			raise ValueError("Wrong value %s for attribute hour" % self.hour)
		if self.minute is not None and not 0 <= self.minute <= 59:
			raise ValueError("Wrong value %s for attribute minute" % self.minute)
		if self.second is not None and not 0 <= self.second <= 59:
			raise ValueError("Wrong value %s for attribute second" % self.second)

	@classmethod
	def from_string(cls, time_string):
		# dateutil parser fills the unknow values from the default
		# We use this to know wich field was set
		one = dateutil.parser.parse(time_string, default = datetime(1,1,1,1,1,1,1))
		two = dateutil.parser.parse(time_string, default = datetime(2,2,2,2,2,2,2))
		time = cls()
		for attr in ["year", "month", "day", "hour", "minute", "second", "microsecond"]:
			if getattr(one, attr) == 1:
				if getattr(two, attr) == 2:
					# The attribute was not set
					setattr(time, attr, None)
				else:
					setattr(time, attr, 1)
			else:
				setattr(time, attr, getattr(two, attr)) 
		
		# Add microseconds to seconds
		if time.microsecond is not None:
			if time.second is None:
				time.second = time.microsecond/1000000.0
			else:
				time.second += time.microsecond/1000000.0
			time.microsecond = None
		
		return time
	
	def __str__(self):
		
		return ", ".join(["%s: %s" % (attr,  getattr(self, attr)) for attr in ["year", "month", "day", "hour", "minute", "second"]])
	
	def __repr__(self):
		
		return "Time(%s)" % str(self)

class Data:
	
	def __init__(self, meta_data, data_location, tags):
		self.meta_data = meta_data
		self.data_location = data_location
		self.tags = tags
	
	def download(self, to="."):
		if os.path.isdir(to):
			to = os.path.join(to, os.path.basename(urlparse.urlparse(self.data_location).path))
		elif not os.path.isdir(os.path.dirname(to)):
			raise ValueError("No directory %s" % os.path.dirname(to))
		
		urllib.urlretrieve(self.data_location, to)
	
	def data(self):
		return StringIO.StringIO(urllib.urlopen(self.data_location).read())


class Dataset:
	
	class Iterator:
	
		def __init__(self, api, filters, keywords, offset = 0, limit = 20):
		
			self.api = api
			self.filters = filters
			self.keywords = keywords
			self.limit = limit
			self.offset = offset
			self.infos = []
		
		def __iter__(self):
			# Iterators are iterables too.
			return self
		
		def next(self):
			# Cache some info
			if not self.infos:
				self.infos = self.api.get(limit=self.limit, offset=self.offset, **self.filters)["objects"]
				self.offset += self.limit
			# Return the first one in cache
			if self.infos:
				info = self.infos.pop(0)
				# Parse the info into a Data
				meta_data = {self.keywords[field_name]: value for field_name, value in info.iteritems() if field_name in self.keywords}
				try:
					data_location = info["data_location"]["url"]
				except TypeError, KeyError:
					data_location = None
				tags = [tag["name"] for tag in info["tags"]]
				return Data(meta_data, data_location, tags)
			else:
				raise StopIteration()
	
	def __init__(self, info, api = API):
		self.name = info["name"]
		self.display_name = info["display_name"]
		self.description = info["description"]
		self.characteristics = info["characteristics"]
		
		self.keyword_api = api.api.v1(self.name + "_keyword")
		self.meta_data_api = api.api.v1(self.name + "_meta_data")
		self.data_location_api = api.api.v1(self.name + "_data_location")
		
		#Set up the keywords and the field names for easy reverse lookup
		self._keywords = dict()
		self._field_names = dict()
		for keyword in self.keyword_api.get(limit=0)["objects"]:
			self._field_names[keyword["name"]] = keyword["db_column"]
			self._keywords[keyword["name"]] = {"description": keyword["description"], "unit": keyword["unit"], "type": keyword["python_type"] }
		
		# At first the filter is empty
		self.filters = dict()
	
	def __str__(self):
		if self.filters:
			return self.display_name + ": " + "; ".join([keyword+" = "+str(value) for keyword,value in self.filters.iteritems()])
		else:
			return self.display_name + ": all"
	
	def __repr__(self):
		return self.name
	
	def __get_filters(self):
		filters = dict()
		for keyword, value in self.filters.iteritems():
			field_name = self._field_names[keyword]
			try:
				if self.keywords[keyword]["type"] == "str":
					filters.update(self.string_filter(field_name, value))
				elif self.keywords[keyword]["type"] == "int" or self.keywords[keyword]["type"] == "float":
					filters.update(self.numeric_filter(field_name, value))
				elif self.keywords[keyword]["type"] == "datetime":
					filters.update(self.time_filter(field_name, value))
				else:
					raise NotImplementedError("Filter for type %s has not been implemented", self.keywords[keyword]["type"])
			except Exception, why:
				raise ValueError("Bad value %s for keyword %s: %s", (keyword, value, why))
	
		return filters
	
	def __iter__(self):
		return self.Iterator(self.meta_data_api, self.__get_filters(), {field_name: keyword for keyword, field_name in self._field_names.iteritems()})
	
	def __getitem__(self, key) :
		if isinstance(key, slice) :
			# TODO if step is very large than cut down in smaller requests
			datas = list()
			i = 0
			for data in self.Iterator(self.meta_data_api, self.__get_filters(), {field_name: keyword for keyword, field_name in self._field_names.iteritems()}, offset = key.start, limit = key.stop):
				if i % key.step == 0:
					datas.append(data)
				i += 1
				if i + key.start >= key.stop:
					break
			return datas
		elif isinstance(key, int) :
			if key < 0:
				raise IndexError("Negative indexes are not supported.")
			else:
				iterator = self.Iterator(self.meta_data_api, self.__get_filters(), {field_name: keyword for keyword, field_name in self._field_names.iteritems()}, offset = key, limit = 1)
				data = iterator.next()
				if data:
					return data
				else:
					raise IndexError("The index (%d) is out of range" % key)
		else:
			raise TypeError("Invalid argument type.")
	
	@property
	def keywords(self):
		return self._keywords
	
	@staticmethod
	def string_filter(field_name, value):
		filters = dict()
		if not isinstance(value, (tuple, list)):
			filters[field_name+"__iexact"] = value
		elif len(value) == 0 or len(value) > 3:
				raise Exception("String filter must either be an exact value or a triplet (starts with, contains, end with)")
		else:
			if len(value) >= 1 and value[0] is not None:
				filters[field_name+"__istartswith"] = value[0]
			if len(value) >= 2 and value[1] is not None:
				filters[field_name+"__icontains"] = value[1]
			if len(value) >= 3 and value[2] is not None:
				filters[field_name+"__iendswith"] = value[2]
		
		return filters
	
	@staticmethod
	def numeric_filter(field_name, value):
		filters = dict()
		if not isinstance(value, (tuple, list)):
			filters[field_name+"__exact"] = value
		elif len(value) == 0 or len(value) > 2:
				raise Exception("Time filter must either be an exact value or a doublet (min value, max value)")
		else:
			if len(value) >= 1 and value[0] is not None:
				filters[field_name+"__gte"] = value[0]
			if len(value) >= 2 and value[1] is not None:
				filters[field_name+"__lt"] = value[1]
		
		return filters
	
	@staticmethod
	def time_filter(field_name, value):
		filters = dict()
		if not isinstance(value, (tuple, list)):
			if isinstance(value, datetime):
				filters[field_name+"__exact"] = value.isoformat()
			else:
				time = Time(value)
				for attr in ["year", "month", "day", "hour", "minute", "second"]:
					if getattr(time, attr) is not None:
						filters[field_name + "__" + attr] = getattr(time, attr)
		elif len(value) == 0 or len(value) > 2:
				raise Exception("Numeric filter must either be an exact value or a doublet (min value, max value)")
		else:
			if len(value) >= 1 and value[0] is not None:
				filters[field_name+"__gte"] = value[0].isoformat()
			if len(value) >= 2 and value[1] is not None:
				filters[field_name+"__lt"] = value[1].isoformat()
		
		return filters
	
	def filter(self, *args, **kwargs):
		filters = dict()
		args = dict(zip(args[::2], args[1::2]))
		args.update(kwargs)
		for keyword, value in args.iteritems():
			if keyword in self._field_names:
				filters[keyword] = value
			else:
				raise LookupError("Unknown keyword %s for dataset %s" % (keyword, self.display_name))
		
		dataset_copy = copy.deepcopy(self)
		dataset_copy.filters.update(filters)
		return dataset_copy


class Datasets:
	
	class Iterator:
	
		def __init__(self, infos, offset = 0, limit = 0):
		
			self.infos = infos
		
		def __iter__(self):
			# Iterators are iterables too.
			return self
		
		def next(self):
			# Return the first one in cache
			if self.infos:
				return Dataset(self.infos.pop(0))
			else:
				raise StopIteration()
	
	def __init__(self, api = API):
		self.api = api.api.v1("dataset")
		self.datasets = [Dataset(info, api) for info in self.api.get(limit=0)["objects"]]
		self._field_names = ["name", "display_name", "instrument", "telescope", "description", "contact", "characteristics"]
		self.filters = dict()
	
	def __iter__(self):
		filters = dict()
		for field_name, value in self.filters.iteritems():
			try:
				filters.update(self.string_filter(field_name, value))
			except Exception, why:
				raise ValueError("Bad value %s for keyword %s: %s", (keyword, value, why))
		
		return self.Iterator(self.api.get(limit=0, **filters)["objects"])
	
	def __str__(self):
		return ", ".join([str(dataset) for dataset in self])
	
	def __repr__(self):
		return ", ".join([repr(dataset) for dataset in self])
	
	def __getitem__(self, key):
		if isinstance(key, (slice, int)):
			return self.datasets[key]
		elif isinstance(key, basestring):
			try:
				return next(dataset for dataset in self.datasets if dataset.name == key or dataset.display_name == key)
			except StopIteration:
				raise IndexError("No such dataset")
		else:
			raise TypeError("Invalid argument type.")
	
	def filter(self, *args, **kwargs):
		filters = dict()
		args = dict(zip(args[::2], args[1::2]))
		args.update(kwargs)
		for keyword, value in args.iteritems():
			if keyword in self._field_names:
				filters[keyword] = value
			else:
				raise LookupError("Unknown keyword %s for datasets" % keyword)
		
		datasets_copy = copy.deepcopy(self)
		datasets_copy.filters.update(filters)
		return datasets_copy
	



datasets = Datasets(API)

