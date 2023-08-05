#!/usr/bin/env python3

"""
TODO:
+ Detectar que no existe en el path
+ Generar uno vacio
- Test default path on windows
- Test default path on mac 
- Getting a missing profile
- Any attribute is null
"""
import os
from .namespace import namespace
from .consolemsg import error


# Kludge in order to use FileNotFoundError in Python2
try: FileNotFoundError
except NameError:
	FileNotFoundError=IOError

class BadProfile(Exception) : pass
class MissingValue(Exception) : pass

_mandatoryKeys = 'dbname user pwd'.split()

def defaultConfigDbFile() :
	import appdirs
	return os.path.join(
		appdirs.user_config_dir(
			appname='configdb',
			appauthor='somenergia',
			version='1.0',
			),
			'configdb.yaml',
		)

def generateDefault(configfile, required=_mandatoryKeys) :
	container = os.path.dirname(configfile)
	if container and not os.access(container, os.R_OK) :
		os.makedirs(os.path.dirname(configfile))
	data=namespace(
		default=namespace(
			(key,None) for key in required
		))
	data.dump(configfile)
	return data

def configdb(configfile=None, profile=None, required=_mandatoryKeys ):

	profile = profile or os.environ.get('CONFIGDB_PROFILE', 'default')

	configfile = configfile or defaultConfigDbFile()

	try :
		data = namespace.load(configfile)
	except FileNotFoundError:
		error(
			"Database configuration file not available, "
			"generating a default one at '{}'"
			.format(configfile))
		data = generateDefault(configfile, required)

	try:
		result = data[profile]
	except KeyError:
		message = ("Database profile '{}' not availabe in '{}'"
			.format(profile, configfile) + (", try with: "+
				(", ".join(sorted(data.keys()))) if data else ""))
		error(message)
		raise BadProfile(message)

	for key in required:
		if key not in result or not result[key] :
			raise MissingValue(key)

	return result



