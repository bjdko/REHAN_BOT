import json
import os
import time
import aiohttp
import asyncio

import requests

import config

# data_tebakan = {}
mabar_tebakan = {}

def generate_template(role, prompt):
    return {"role": role, "parts": [{"text": prompt}]}


def reset_tebakan():
    # global data_tebakan
    data_tebakan = {
        "system_instruction": {
            "parts": {
                "text": ""
            }
        },
        "contents": [],
    }


def tebakan(prompt, userid):
    # global data_tebakan
    headers = {"Content-Type": "application/json"}
    data_tebakan["contents"].append(generate_template("user", prompt))
    response = requests.post(config.API_URL,
                             headers=headers,
                             json=data_tebakan,
                             params={"key": config.API_KEY})
    while response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))
        print(f"Rate limited. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)
        response = requests.post(config.API_URL,
                                 headers=headers,
                                 json=data_tebakan,
                                 params={"key": config.API_KEY})
    response_json = response.json()
    if "candidates" in response_json:
        candidate = response_json["candidates"][0]
        if "content" in candidate:
            response_text = candidate["content"]["parts"][0]["text"]
            data_tebakan["contents"].append(
                generate_template("model", response_text))
            directory = "./data/history"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = f"{directory}/{userid}_sesitebakan.json"
            with open(filename, 'w') as file:
                json.dump(data_tebakan, file)
            return split_string(response_text)
        elif candidate.get("finishReason") == "SAFETY":
            # Handle safety stop
            return ["The response was stopped due to safety concerns."]
        else:
            # Handle other cases
            return ["The response was stopped due to an unknown reason."]
    else:
        error_message = response_json.get('error',
                                          {}).get('message',
                                                  'Unknown error occurred')
        print(f"Error: {error_message}")
        return [f"Sorry, I couldn't process your request: {error_message}"]


async def chat_ai(userid, prompt):
    _data = load(userid)
    _data["contents"].append(generate_template("user", prompt))
    response_json = await asinkronus_bard(_data)
    return await safety_check_etc(response_json)


def split_string(kalimat_panjang):
    messages = []
    if len(kalimat_panjang) > 2000:
        kata = kalimat_panjang.split()
        pesan_sekarang = ""
        for kata_sekarang in kata:
            if len(pesan_sekarang + kata_sekarang) + 1 > 2000:
                messages.append(pesan_sekarang)
                pesan_sekarang = kata_sekarang
            else:
                if pesan_sekarang:
                    pesan_sekarang += " " + kata_sekarang
                else:
                    pesan_sekarang = kata_sekarang
        if pesan_sekarang:
            messages.append(pesan_sekarang)
    else:
        messages.append(kalimat_panjang)
    return messages


def load(userid):
    filename = f"./data/history/{userid}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            _data = json.load(file)
    else:
        _data = {
            "system_instruction": {
                "parts": {
                    "text": ""
                }
            },
            "contents": [],
        }
    return _data


def save(userid, _data):
    directory = "./data/history"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"{userid}.json")
    with open(filename, 'w') as file:
        json.dump(_data, file)


def reset_data(userid):
    filename = f"./data/history/{userid}.json"
    if os.path.exists(filename):
        os.remove(filename)


async def react(prompt):
    with open("./data/emoji_data.json", "r") as bvedrfcg:
        libraryge = json.load(bvedrfcg)
    _sementara = []
    for i in libraryge:
        current_key_dict = libraryge[i]
        _sementara.append(
            f"emote name: {i},\nemote description: {current_key_dict['emote_description']}"
        )
    tambahan = f"what emote would you react with that fit with this \"{prompt}\"? Choose the emote based on the \
    description but not too perfectly matched. Reply with just emote name without saying anything else"

    initial_msg = "\n\n".join(_sementara)
    jawab = await ask_emoji(initial_msg, tambahan)
    ribet = jawab[0].strip()
    for emot in libraryge:
        if emot.lower() == ribet.lower():
            return libraryge[emot]["emote_url"]
    return "Gatau"


async def ask_emoji(initial_msg, actual_msg):
    headers = {"Content-Type": "application/json"}

    payload = {"contents": [{"parts": [{"text": initial_msg + "\n" + actual_msg}]}]}
    response_json = await asinkronus_bard(payload, config.API_URL_2)
    return await safety_check_etc(response_json)


async def one_timers(prompt):
    jason = {
        "system_instruction": {
            "parts": {"text": "useful assistant, solid and concise and clear"}
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    response_json = await asinkronus_bard(jason)
    return await safety_check_etc(response_json)


async def asinkronus_bard(_json, api_url=config.API_URL):
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        retry_count = 0
        while retry_count < 5:
            async with session.post(api_url, headers=headers, json=_json,
                                    params={"key": config.API_KEY}) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    retry_count += 1
                else:
                    return await response.json()
                print(f"retry_count limit exceeded (5x) xddinside")


async def safety_check_etc(response_json):
    if "candidates" in response_json:
        candidate = response_json["candidates"][0]
        if "content" in candidate:
            response_text = candidate["content"]["parts"][0]["text"]
            return split_string(response_text)
        elif candidate.get("finishReason") == "SAFETY":
            # Handle safety stop
            return ["The response was stopped due to safety concerns."]
        else:
            # Handle other cases
            return ["The response was stopped due to an unknown reason."]
    else:
        error_message = response_json.get('error',
                                          {}).get('message',
                                                  'Unknown error occurred')
        print(f"Error: {error_message}")
        return [f"Sorry, I couldn't process your request: {error_message}"]


async def acting(userid, prompt):
    _data = load(userid)
    _data["system_instruction"]["parts"]["text"] = f"you shall act as {prompt}"
    _data["contents"].append(generate_template("user", prompt))
    response_json = await asinkronus_bard(_data)
    print(response_json)
    if "candidates" in response_json:
        candidate = response_json["candidates"][0]
        if "content" in candidate:
            response_text = candidate["content"]["parts"][0]["text"]
            _data["contents"].append(generate_template("model", response_text))
            save(userid, _data)
    return await safety_check_etc(response_json)