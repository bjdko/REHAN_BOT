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
xddinside___ = None


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    logging.info(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    global xddinside___
    if message.author.bot:
        return
    # NGECEK JAWABAN
    if xddinside___:
        if message.reference:
            _fetchge = await message.channel.fetch_message(xddinside___.reference.message_id)
            _id_original_penanya = _fetchge.author.id
            if xddinside___ and message.reference.message_id == xddinside___.id:
                if message.author.id == _id_original_penanya:
                    jawaban = message.content
                    async with message.channel.typing():
                        adalah_ai = bard.tebakan(jawaban, message.author.id)
                        for pesan in adalah_ai:
                            xddinside___ = None
                            await message.channel.send(pesan)

                    filename = f"./data/history/{message.author.id}_sesitebakan.json"
                    if os.path.exists(filename):
                        bard.reset_tebakan()
                        os.remove(filename)
                else:
                    await message.reply(f"Twas not thou who didst inquire, cur, but <@{_id_original_penanya}>",
                                        mention_author=False)

    # NGECCEK FILE
    _waktu_sekarang = time.time()
    _history_location = "data/history"
    history_list = os.listdir(_history_location)
    for filege in history_list:
        _filege_full_path = os.path.join(_history_location, filege)
        if filege.endswith("_sesitebakan.json"):
            _umur_file = _waktu_sekarang - os.path.getctime(_filege_full_path)
            if _umur_file >= 300:
                bard.reset_tebakan()
                os.remove(_filege_full_path)
                xddinside___ = None
        else:
            _umur_file = _waktu_sekarang - os.path.getctime(_filege_full_path)
            if _umur_file >= 86400:
                os.remove(_filege_full_path)
    await bot.process_commands(message)


# ==========ONE TIME ASKs==========
@bot.command()
async def ask(ctx, *, promptge: str = ""):
    if not promptge:
        await ctx.send("nanaonan")
        return
    async with ctx.typing():
        adalah_ai = await bard.one_timers(promptge)
        for i in adalah_ai:
            await ctx.reply(i, mention_author=False)


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
            await ctx.reply(i, mention_author=False)


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
    global xddinside___
    if not tema:
        tema = "apapun"
    userid = ctx.author.id
    if not xddinside___:
        async with ctx.typing():
            adalah_ai = bard.tebakan(
                f"beri saya tebak-tebakan yang bertema materi {tema} dan saya akan menjawabnya dengan gaya bahasa \
                saya sendiri. Berdasarkan jawaban yang saya beri, jawab benar atau salahnya dan jelaskan jawaban \
                benarnya. Sebagai tambahan lagi, saya hanya diberi 1 kesempatan jangan dikasih lebih, salah atau benar \
                jawaban saya akhiri saja tebak-tebakannya",
                userid)
            memek = 0
            for i in adalah_ai:
                if memek == 0:
                    ngetescoy = "__**Pake fitur reply di discord buat jawab coy.**__\n\n" + i
                    memek += 1
                    xddinside___ = await ctx.reply(ngetescoy, mention_author=False)
                else:
                    xddinside___ = await ctx.reply(i, mention_author=False)
    else:
        _channel = bot.get_channel(xddinside___.reference.channel_id)
        _fetchge = await _channel.fetch_message(xddinside___.reference.message_id)
        await ctx.reply(f"lagi mainin <@{_fetchge.author.id}>.",
                        mention_author=False)


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
    prompt = '''
        Buatlah daftar panduan untuk penggunaan bot, saya akan memberikan perintah dan apa yang harus Anda berikan/perluas untuk penjelasan masing-masing perintah.
        Berikut daftarnya:
        .chat = beri tahu pengguna bahwa perintah ini untuk mengobrol dengan bot dan bot akan mengingat Anda. Contoh: .chat Can you daydream at night?.
        .ask = memberi tahu pengguna bahwa perintah ini untuk bertanya kepada bot dan bot TIDAK akan mengingat Anda. Contoh: .ask Who is Pedro?.
        .act = memberi tahu pengguna bahwa perintah ini untuk mengatur bot bagaimana seharusnya bertindak. Contoh: .act sebagai
        .reset = memberi tahu pengguna bahwa perintah ini untuk mengatur ulang bot, perintah ini akan menghapus memori bot agar tidak riwayat Anda.
        .react = memberi tahu pengguna bahwa perintah ini untuk bereaksi dengan emoticon terhadap perintah yang Anda berikan. Contoh: .react aku terjatuh dan tak bisa bangun lagi
    '''
    _orig = await ctx.reply("`.chat`\n`.ask`\n`.act`\n`.reset`\n`.react`\n",
                            mention_author=False)
    async with ctx.typing():
        adalah_ai = bard.one_timers(prompt)
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
