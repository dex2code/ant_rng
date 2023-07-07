from config import *
from loguru import logger
from flask import Flask, render_template
import json, hashlib


ant_app = Flask(__name__, static_url_path='/static')
ant_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
ant_app.config['TEMPLATES_AUTO_RELOAD'] = True


@ant_app.route('/')
@logger.catch
def app_root():
    with open(f"{RESULT_DIR}/{RESULT_JSON_NAME}", "rt") as input_file:
        json_string = input_file.read()
    parsed_json = json.loads(json_string)

    seed_str = ""
    for c in parsed_json['coordinates']:
        seed_str += str(c)

    seed_str += str(parsed_json['uuid'])
    seed_str += str(parsed_json['timestamp'])

    s = hashlib.sha3_512()
    s.update(seed_str.encode())
    my_hash_str = s.hexdigest()
    my_hash_bytes = s.digest()
    my_hash_int = int.from_bytes(my_hash_bytes, "big")

    rnd_array = []

    while my_hash_int:
        rnd_array.append(my_hash_int % NUMBER_DIGITS)
        my_hash_int = my_hash_int // NUMBER_DIGITS

    return render_template('index.html', parsed_json=parsed_json, h="0x" + my_hash_str, rnd_array=rnd_array)


@ant_app.route('/api')
@logger.catch
def app_api():
    api_result = {}

    with open(f"{RESULT_DIR}/{RESULT_JSON_NAME}", "rt") as input_file:
        json_string = input_file.read()
    parsed_json = json.loads(json_string)

    seed_str = ""
    for c in parsed_json['coordinates']:
        seed_str += str(c)

    seed_str += str(parsed_json['uuid'])
    seed_str += str(parsed_json['timestamp'])

    s = hashlib.sha3_512()
    s.update(seed_str.encode())
    my_hash_str = s.hexdigest()
    my_hash_bytes = s.digest()
    my_hash_int = int.from_bytes(my_hash_bytes, "big")

    rnd_array = []
    while my_hash_int:
        rnd_array.append(my_hash_int % NUMBER_DIGITS)
        my_hash_int = my_hash_int // NUMBER_DIGITS

    api_result["uuid"] = str(parsed_json['uuid'])
    api_result["timestamp"] = parsed_json['timestamp']
    api_result["coordinates"] = parsed_json['coordinates']
    api_result["sha3"] = "0x" + my_hash_str
    api_result["rnd"] = rnd_array

    return api_result


if __name__ == "__main__":
    ant_app.run()
