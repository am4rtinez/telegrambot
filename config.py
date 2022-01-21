from os import path
from os import environ as env
from dotenv import load_dotenv

# Obtine el directorio principal
basedir = path.abspath(path.dirname(__file__))
# Genera el path del fichero .env
load_dotenv(path.join(basedir, '.env'))

API_KEY = env['API_KEY']
