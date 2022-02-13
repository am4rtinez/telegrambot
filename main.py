import telebot
from telebot import types
import requests
import json
import config

API_KEY = config.API_KEY
URL_CCAA_LIST = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/ComunidadesAutonomas/"
URL_PROV_LIST = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Provincias/"
URL_MUN_LIST = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Municipios/"

bot = telebot.TeleBot(API_KEY)

data_dict = {}


class Data:
    def __init__(self, ccaa):
        self.id_ccaa = ccaa
        self.ccaa_desc = None
        self.id_prov = None
        self.prov_desc = None
        self.id_mun = None
        self.mun_desc = None


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to FrikiBot!")


@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, """
The following commands are available:
    
/start -> Inicia el bot.
/help -> Ayuda del bot.
/ccaa -> Muestra el listado de Comunidades Autonomas.
/provincias -> Muestra el listado de provincias.
/municipios -> Muestra el listado de municipios.
/config - Configura las preferencias del usuario (CCAA/Provincia/Municipio).
/info - Muestra las preferencias del usuario.
    """)


@bot.message_handler(commands=['ccaa'])
def ccaa(message):
    ccaa_list = "Listado Comunidades Autonomas: \n"
    for item in dict_ccaa:
        ccaa_list = ccaa_list + item['IDCCAA'] + " - " + item['CCAA'] + "\n"
    bot.reply_to(message, ccaa_list)


@bot.message_handler(commands=['provincias'])
def provincias(message):
    prov_list = "Listado Provincias: \n"
    for item in dict_provincias:
        prov_list = prov_list + item['IDPovincia'] + \
            " - " + item['Provincia'] + "\n"
    bot.reply_to(message, prov_list)


@bot.message_handler(commands=['provincias'])
def provincias(message):
    pass


@bot.message_handler(commands=['config'])
def set_config(message):

    # Compone el mensaje con el listado de CCAA.
    lista = "Seleccione CCAA: \n"
    for item in dict_ccaa:
        lista = lista + item['IDCCAA'] + " - " + item['CCAA'] + "\n"
    markup = types.ReplyKeyboardMarkup(row_width=1)
    msg = bot.reply_to(message, lista, reply_markup=markup)
    bot.register_next_step_handler(msg, process_ccaa_step)


@bot.message_handler(commands=['info'])
def config(message):
    try:
        chat_id = message.chat.id
        data = data_dict[chat_id]
        msg = data.id_ccaa + " " + data.id_prov + " " + data.id_mun
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, 'No config found')


def get_content(url):
    '''
    | Obtiene el contenido de la url y lo transforma a json.
    '''
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Access-Control-Allow-Origin': '*'}
    content = None
    # Get content
    r = requests.get(url, headers=headers)
    # Decode JSON response into a Python dict:
    content = r.json()
    return content


def process_ccaa_step(message):
    try:
        chat_id = message.chat.id
        ccaa = message.text
        data = Data(ccaa)
        data_dict[chat_id] = data

        # Obtiene el listado de las Provincias pertenecientes a la Comunidad Autonoma.
        url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/ProvinciasPorComunidad/"
        json_data = get_content(f'{url}{data.id_ccaa}')
        # Compone el mensaje con el listado de Provincias de las CCAA.
        lista = "Seleccione Provincia: \n"
        for item in json_data:
            lista = lista + item['IDPovincia'] + \
                " - " + item['Provincia'] + "\n"

        markup = types.ReplyKeyboardMarkup(row_width=1)
        msg = bot.reply_to(message, lista, reply_markup=markup)
        bot.register_next_step_handler(msg, process_provincia_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_provincia_step(message):
    try:
        chat_id = message.chat.id
        idprov = message.text
        data = data_dict[chat_id]
        data.id_prov = idprov

        url = 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/MunicipiosPorProvincia/'
        json_data = get_content(f'{url}{idprov}')
        # Compone el mensaje con el listado de Municipios.
        lista = "Seleccione Municipio: \n"
        for item in json_data:
            lista = lista + item['IDMunicipio'] + \
                " - " + item['Municipio'] + "\n"
        markup = types.ReplyKeyboardMarkup(row_width=1)
        msg = bot.reply_to(message, lista, reply_markup=markup)
        bot.register_next_step_handler(msg, process_municipio_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_municipio_step(message):
    try:
        chat_id = message.chat.id
        data = data_dict[chat_id]
        idmun = message.text
        data.id_mun = idmun
        url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipio/"
        json_data = get_content(f'{url}{idmun}')
        # msg = bot.reply_to(message, "Procesada la info")
        bot.send_message(chat_id, data.id_ccaa + " " +
                         data.id_prov + " " + data.id_mun)

    except Exception as e:
        bot.reply_to(message, e)


def process_config_step(message):
    try:
        chat_id = message.chat.id
        data = data_dict[chat_id]
        msg = data.id_ccaa + " " + data.id_prov + " " + data.id_mun
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, 'oooops')


if __name__ == '__main__':
    dict_ccaa = get_content(URL_CCAA_LIST)
    dict_provincias = get_content(URL_PROV_LIST)
    dict_municipios = get_content(URL_MUN_LIST)
    bot.polling()
