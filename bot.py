import logging
import os
import time

import discord
from discord.ext import commands

import config
from local_utils import bard

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/bot.log',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

mabar_tebakan = {}


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    logging.info(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    global mabar_tebakan
    if message.author.bot:
        return
    # NGECEK JAWABAN
    if message.reference and mabar_tebakan[message.author.id]:
        _id_penjawab = message.author.id
        _data_tebakan = mabar_tebakan[_id_penjawab]
        for _tebak_ctx in _data_tebakan["CTXs"]:
            if message.reference.message_id == _tebak_ctx.id:
                _fetch_penanya = await message.channel.fetch_message(_data_tebakan["CTXs"][0].reference.message_id)
                async with message.channel.typing():
                    if _id_penjawab == _fetch_penanya.author.id:
                        _data_tebakan["data"]["contents"].append(bard.generate_template("user", message.content))
                        __response_json = await bard.asinkronus_bard(_data_tebakan["data"])
                        __adalah_ai = await bard.safety_check_etc(__response_json)
                        for _ in __adalah_ai:
                            if _ == __adalah_ai[0]:
                                __ = await message.reply(_, mention_author=False)
                            else:
                                await __.reply(_, mention_author=False)
                        del mabar_tebakan[_id_penjawab]

    # NGECCEK FILE
    _waktu_sekarang = time.time()
    _history_location = "./data/history"
    history_list = os.listdir(_history_location)
    for filege in history_list:
        _filege_full_path = os.path.join(_history_location, filege)
        _umur_file = _waktu_sekarang - os.path.getmtime(_filege_full_path)
        if _umur_file >= 21600:
            os.remove(_filege_full_path)
    await bot.process_commands(message)


# ==========ONE TIME ASKs==========
@bot.command()
async def ask(ctx, *, promptge: str = ""):
    userid = ctx.author.id
    prefix = ""
    if not promptge:
        await ctx.send("nanaonan")
        return

    if os.path.exists(f"./data/history/{userid}.json"):
        prefix = "||__Menggunakan **act**.__||\n"
    async with ctx.typing():
        adalah_ai = await bard.one_timers(promptge, userid)
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await ctx.reply(prefix + i, mention_author=False)
            else:
                await _orig.reply(i, mention_author=False)


# ==========CHAT BOT==========
@bot.command()
async def chat(ctx, *, promptge: str = ""):
    userid = ctx.author.id
    if not promptge:
        await ctx.send("Huh?")
        return
    async with ctx.typing():
        adalah_ai = await bard.chat_ai(userid, promptge)
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await ctx.reply(i, mention_author=False)
            else:
                _orig = await _orig.reply(i, mention_author=False)


# ==========ACT==========
@bot.command()
async def act(ctx, *, promptge: str):
    userid = ctx.author.id
    adalah_ai = await bard.acting(userid, promptge)
    await ctx.reply(adalah_ai[0], mention_author=False)


# ==========RESET==========
@bot.command()
async def reset(ctx):
    userid = ctx.author.id
    kanjut = await ctx.reply("bntar", mention_author=False)
    async with ctx.typing():
        adalah_ai = await bard.chat_ai(userid, "I will reset you. Goodbye!")
        bard.reset_data(userid)
        for i in adalah_ai:
            await kanjut.edit(content=i)
            break


# ==========QUIZ==========
@bot.command()
async def tebak(ctx, *, tema: str = None):
    global mabar_tebakan
    _orig = ctx
    if not tema:
        tema = "apapun"
    userid = ctx.author.id
    _tebakan_data = {
        "timestamp": time.time(),
        "CTXs": [],
        "data": {
            "system_instruction": {
                "parts": {
                    "text": ""
                }
            },
            "contents": [],
        }
    }
    mabar_tebakan[userid] = _tebakan_data
    _tebakan_history = _tebakan_data["data"]["contents"]
    _CTXs = _tebakan_data["CTXs"]
    async with ctx.typing():
        adalah_ai = await bard.one_timers(f"kamu hanya cukup sebutkan pertanyaannya, beri saya tebak-tebakan yang "
                                          f"bertema materi {tema} dan saya akan menjawabnya dengan gaya bahasa saya "
                                          f"sendiri. Berdasarkan jawaban yang saya beri, jawab benar atau salahnya "
                                          f"dan jelaskan jawaban benarnya. Sebagai tambahan lagi, saya hanya diberi 1 "
                                          f"kesempatan jangan dikasih lebih, salah atau benar jawaban saya akhiri "
                                          f"saja tebak-tebakannya")
        _tebakan_history.append(bard.generate_template("model", " ".join(adalah_ai)))
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await ctx.reply("__**Pake fitur reply di discord buat jawab coy.**__\n\n" + i,
                                        mention_author=False)
                _CTXs.append(_orig)
            else:
                _orig = await _orig.reply(i, mention_author=False)
                _CTXs.append(_orig)


@bot.command()
async def react(ctx, *, promptge: str = ""):
    if not promptge:
        await ctx.send("nanaonan")
        return
    async with ctx.typing():
        adalah_ai = await bard.react(promptge)
        await ctx.reply(adalah_ai, mention_author=False)


@bot.command()
async def tolong(ctx):
    prompt = '''Buatlah daftar panduan untuk penggunaan bot, saya akan memberikan perintah dan apa yang harus Anda berikan/perluas untuk penjelasan masing-masing perintah.
Berikut daftarnya:
.chat = beri tahu pengguna bahwa perintah ini untuk mengobrol dengan bot dan bot akan mengingat Anda. Contoh: .chat Can you daydream at night?.
.ask = memberi tahu pengguna bahwa perintah ini untuk bertanya kepada bot dan bot TIDAK akan mengingat Anda. Contoh: .ask Who is Pedro?.
.act = memberi tahu pengguna bahwa perintah ini untuk mengatur bot bagaimana seharusnya bertindak. Contoh: .act sebagai forsen. Dan gunakan command .act tanpa memberikan parameter untuk reset
.reset = memberi tahu pengguna bahwa perintah ini untuk mengatur ulang bot, perintah ini akan menghapus memori termasuk act dan riwayat khusus untuk anda
.react = memberi tahu pengguna bahwa perintah ini untuk bereaksi dengan emoticon terhadap perintah yang Anda berikan. Contoh: .react aku terjatuh dan tak bisa bangun lagi
'''
    _orig = await ctx.reply("`.chat`\n`.ask`\n`.act`\n`.reset`\n`.react`\n",
                            mention_author=False)
    async with ctx.typing():
        adalah_ai = await bard.one_timers(prompt)
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await _orig.edit(content=i)
            else:
                await _orig.reply(i, mention_author=False)


@bot.command()
async def a(ctx):
    await ctx.send("b")


def main():
    bot.run(config.TOKEN_BOT)
