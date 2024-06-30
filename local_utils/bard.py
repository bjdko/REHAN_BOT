import json
import os
import time
import aiohttp
import asyncio

import requests

import config

from typing import Literal


# data_tebakan = {}


def generate_template(role: Literal["user", "model"], prompt: str):
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


async def chat_ai(userid, prompt):
    _data = load(userid)
    _data["contents"].append(generate_template("user", prompt))
    response_json = await asinkronus_bard(_data)
    save(userid, _data)
    return await safety_check_etc(response_json)


def split_string(kalimat_panjang, max_length=1900):
    chunks = []
    current_chunk = ""
    words = kalimat_panjang.split()

    for word in words:
        # Periksa apakah penambahan kata sesuai dengan panjang maksimal
        if len(current_chunk) + 1 + len(word) <= max_length:
            current_chunk += " " + word if current_chunk else word
        else:
            # Jika tidak sesuai, tambahkan potongan saat ini ke daftar dan mulai yang baru
            chunks.append(current_chunk)
            current_chunk = word

    # Tambahkan bagian terakhir kl g kosong
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


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
    payload = {"contents": [{"parts": [{"text": initial_msg + "\n" + tambahan}]}]}
    response_json = await asinkronus_bard(payload, config.API_URL_2)
    jawab = await safety_check_etc(response_json)
    ribet = jawab[0].strip()
    for emot in libraryge:
        if emot.lower() == ribet.lower():
            return libraryge[emot]["emote_url"]
    return "Gatau"


async def one_timers(prompt, userid=None):
    jason = {
        "system_instruction": {
            "parts": {"text": "useful assistant, solid and concise and clear"}
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    if userid:
        if os.path.exists(f"./data/history/{userid}.json"):
            _ass = load(userid)
            jason["system_instruction"]["parts"]["text"] = _ass["system_instruction"]["parts"]["text"]

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
    if "candidates" in response_json:
        candidate = response_json["candidates"][0]
        if "content" in candidate:
            response_text = candidate["content"]["parts"][0]["text"]
            _data["contents"].append(generate_template("model", response_text))
            save(userid, _data)
    return await safety_check_etc(response_json)
