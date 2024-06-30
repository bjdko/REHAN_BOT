import asyncio
import json
import os
from typing import Literal

import aiohttp

import config

history_path = "./data/history"
os.makedirs(history_path, exist_ok=True)


def generate_template(role: Literal["user", "model"], prompt: str):
    return {"role": role, "parts": [{"text": prompt}]}


async def chat_ai(userid, prompt):
    _data = load(userid)
    _data["contents"].append(generate_template("user", prompt))
    response_json = await asinkronus_bard(_data)
    response_text = safety_check_etc(response_json)
    _data["contents"].append(generate_template("model", response_text))
    save(userid, _data)
    return split_string(response_text)


def split_string(kalimat_panjang, max_length=1900):
    messages = []
    if len(kalimat_panjang) > max_length:
        kata = kalimat_panjang.split()
        pesan_sekarang = ""
        for kata_sekarang in kata:
            if len(pesan_sekarang + kata_sekarang) + 1 > max_length:
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
    filename = f"{history_path}/{userid}.json"
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
    os.makedirs(history_path, exist_ok=True)
    filename = f"{history_path}/{userid}.json"
    with open(filename, 'w') as file:
        json.dump(_data, file)


def reset_data(userid):
    filename = f"{history_path}/{userid}.json"
    if os.path.exists(filename):
        os.remove(filename)
    load(userid)


async def react(prompt):
    os.makedirs("./data", exist_ok=True)
    emote_data_path = "./data/emoji_data.json"
    if not os.path.exists(emote_data_path):
        return "Gatau"

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
    payload = {"contents": [{"parts": [{"text": initial_msg + "\n" + tambahan}]}]}
    response_json = await asinkronus_bard(payload, config.API_URL_2)
    jawab = safety_check_etc(response_json)
    ribet = jawab.strip()
    for emot in libraryge:
        if emot.lower() == ribet.lower():
            return libraryge[emot]["emote_url"]
    return "Gatau"


async def instant_one_timers(prompt=None, userid=None, jason=None):
    if not jason:
        jason = {
            "system_instruction": {
                "parts": {"text": "useful assistant, solid and concise and clear"}
            },
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        }

    if userid:
        if os.path.exists(f"{history_path}/{userid}.json"):
            _ass = load(userid)
            jason["system_instruction"]["parts"]["text"] = _ass["system_instruction"]["parts"]["text"]

    response_json = await asinkronus_bard(jason)
    response_text = safety_check_etc(response_json)
    return split_string(response_text)


async def asinkronus_bard(_json, api_url=config.API_URL):
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        retry_count = 0
        while retry_count < 100:
            async with session.post(api_url, headers=headers, json=_json,
                                    params={"key": config.API_KEY}) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    retry_count += 1
                else:
                    return await response.json()
        print(f"tried and fails {retry_count}x times")


def safety_check_etc(response_json: dict) -> str:
    if "candidates" in response_json:
        candidate = response_json["candidates"][0]
        if "content" in candidate:
            response_text = candidate["content"]["parts"][0]["text"]
            return response_text
        elif candidate.get("finishReason") == "SAFETY":
            # Handle safety stop
            return "The response was stopped due to safety concerns."
        else:
            # Handle other cases
            return "The response was stopped due to an unknown reason."
    else:
        error_message = response_json.get('error',
                                          {}).get('message',
                                                  'Unknown error occurred')
        print(f"Error: {error_message}")
        return f"Sorry, I couldn't process your request: {error_message}"


async def acting(userid, prompt):
    _data = load(userid)
    _data["system_instruction"]["parts"]["text"] = f"you shall act as {prompt}"
    _data["contents"].append(generate_template("user", prompt))
    response_json = await asinkronus_bard(_data)
    if "candidates" in response_json:
        candidate = response_json["candidates"][0]
        if "content" in candidate:
            response_text = candidate["content"]["parts"][0]["text"]
            _data["contents"].append(generate_template("model", response_text))
            save(userid, _data)
    return split_string(safety_check_etc(response_json))
