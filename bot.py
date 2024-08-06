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
bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents, help_command=None)

mabar_tebakan = {}


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name=".tolong"))
    logging.info(f'Logged in as {bot.user}')
    print(f"{bot.user} is ready and online!")


@bot.event
async def on_message(message):
    global mabar_tebakan
    if message.author.bot:
        return

    # //------ NGECEK HISTORY FILE ------
    _waktu_sekarang = time.time()
    _history_location = "./data/history"
    history_list = os.listdir(_history_location)
    for filege in history_list:
        _filege_full_path = os.path.join(_history_location, filege)
        _umur_file = _waktu_sekarang - os.path.getmtime(_filege_full_path)
        if _umur_file >= 21600:
            userid_from_file, _ = os.path.splitext(filege)
            bard.reset_data(userid_from_file)

    # //------ DELETE TEBAKAN DICT ------
    for key in list(mabar_tebakan.keys()):
        _umur_tebakan = _waktu_sekarang - mabar_tebakan[key]["timestamp"]
        if _umur_tebakan >= 300:
            del mabar_tebakan[key]

    # //------ NGECEK JAWABAN ------
    if message.reference and mabar_tebakan:
        _id_penjawab = message.author.id
        _data_tebakan = mabar_tebakan[_id_penjawab]
        if mabar_tebakan[_id_penjawab]:
            for _tebak_ctx in _data_tebakan["CTXs"]:
                if message.reference.message_id == _tebak_ctx.id:
                    _fetch_penanya = await message.channel.fetch_message(_data_tebakan["CTXs"][0].reference.message_id)
                    async with message.channel.typing():
                        if _id_penjawab == _fetch_penanya.author.id:
                            _data_tebakan["data"]["contents"].append(bard.generate_template("user", message.content))
                            __adalah_ai = await bard.instant_one_timers(jason=_data_tebakan["data"])
                            for _ in __adalah_ai:
                                if _ == __adalah_ai[0]:
                                    __ = await message.reply(_, mention_author=False)
                                else:
                                    await __.reply(_, mention_author=False)
            del mabar_tebakan[_id_penjawab]

    # //------ TWITTER EMBBEDERRERER ------
    if (message.content.startswith("https://twitter.com/") or message.content.startswith("https://x.com/") or
            message.content.startswith("https://nitter.net/")):
        _twitterlink = message.content
        _new_link = _twitterlink.replace("https://twitter.com/", "https://vxtwitter.com/")
        _new_link = _new_link.replace("https://x.com/", "https://vxtwitter.com/")
        _new_link = _new_link.replace("https://nitter.net/", "https://vxtwitter.com/")
        await message.reply(f"{message.author.display_name}:\n{_new_link}", mention_author=False)
        await message.delete()

    # //------ PROCEED ------
    try:
        from local_utils import secret_weapon
        await secret_weapon.secret_command(message)
    except ImportError:
        secret_weapon = "if you see this vivon zulul"

    await bot.process_commands(message)


# ==========ONE TIME ASKs==========
@bot.command()
async def one(ctx, *, promptge: str = ""):
    userid = ctx.author.id
    prefix = ""
    _instruction = ""
    if not promptge:
        await ctx.send("nanaonan")
        return

    if os.path.exists(f"./data/history/{userid}.json"):
        _ass = bard.load(userid)
        _instruction = _ass["system_instruction"]["parts"]["text"]
        _clean_instruction = _instruction.replace('_Act ', '').strip()
        if _clean_instruction:
            prefix = f"||__Menggunakan **act** {_clean_instruction}__||\n"
    async with ctx.typing():
        adalah_ai = await bard.instant_one_timers(promptge, act=_instruction)
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await ctx.reply(prefix + i, mention_author=False)
            else:
                await _orig.reply(i, mention_author=False)


# ==========CHAT BOT==========
@bot.command(name="ask", aliases=["chat"])
async def ask(ctx, *, promptge: str = ""):
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
async def act(ctx, *, promptge: str = ""):
    userid = ctx.author.id
    async with ctx.typing():
        adalah_ai = await bard.acting(userid, promptge)
        await ctx.reply(adalah_ai[0], mention_author=False)


# ==========RESET==========
@bot.command()
async def reset(ctx):
    userid = ctx.author.id
    kanjut = await ctx.reply("dah reset", mention_author=False)
    async with ctx.typing():
        _before_deletion = bard.load(userid)
        bard.reset_data(userid)
        # noinspection PyBroadException
        try:
            _before_deletion["contents"].append(
                bard.generate_template("user", "This is the end of conversation. not possible to chat again"))
            adalah_ai = await bard.instant_one_timers(jason=_before_deletion)
        except:
            adalah_ai = ["dah reset"]
        await kanjut.edit(content=adalah_ai[0])


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
        with open("data/tebakan_string.txt", "r") as f:
            adalah_ai = await bard.instant_one_timers(f.read()+f"tema yang diminta adalah tentang:{tema}")
        _tebakan_history.append(bard.generate_template("model", " ".join(adalah_ai)))
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await ctx.reply("__**Pake fitur reply di discord buat jawab coy.**__\n\n" + i,
                                        mention_author=False)
                _CTXs.append(_orig)
            else:
                _orig = await _orig.reply(i, mention_author=False)
                _CTXs.append(_orig)


# ==========REACT==========
@bot.command()
async def react(ctx, *, promptge: str = ""):
    if not promptge:
        await ctx.send("nanaonan")
        return
    async with ctx.typing():
        adalah_ai = await bard.react(promptge)
        await ctx.reply(adalah_ai, mention_author=False)


# ==========HELP GUIDE==========
@bot.command()
async def tolong(ctx):
    pre_prompt = f"the bot is *'{ctx.guild.me.display_name}'*. "
    with open("data/help_string.txt", "r") as f:
        prompt = pre_prompt + f.read()
    _orig = await ctx.reply("".join(["`."+name+"`\n" for name in bot.all_commands.keys()]),
                            mention_author=False)
    async with ctx.typing():
        adalah_ai = await bard.instant_one_timers(prompt)
        for i in adalah_ai:
            if i == adalah_ai[0]:
                _orig = await _orig.edit(content=i)
            else:
                await _orig.reply(i, mention_author=False)


# ==========YOINK HIJACK==========
@bot.command()
async def yoink(ctx, _mention="", *, promptge: str = ""):
    yoinked_id = ctx.message.mentions[0].id
    if not os.path.exists(f"data/history/{yoinked_id}.json") or not promptge:
        return await ctx.reply("nothing to yoink", mention_author=False)
    else:
        _data = bard.load(yoinked_id)
        _data["contents"].append(bard.generate_template("user", promptge))
        async with ctx.typing():
            adalah_ai = await bard.instant_one_timers(jason=_data)
            for i in adalah_ai:
                if i == adalah_ai[0]:
                    _orig = await ctx.reply(i, mention_author=False)
                else:
                    await _orig.reply(i, mention_author=False)


@bot.command()
async def p(ctx, force_id=None):
    author_id = ctx.author.id
    if ctx.author.id == 228098253143408640:
        if force_id:
            author_id = int(force_id)

    def _pretty(d, indent=2):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                _pretty(value, indent + 1)
            else:
                print('\t' * (indent + 1) + str(value))

    _pretty(bard.load(author_id))
    filenya = "data/history/" + str(author_id) + ".json"
    if os.path.exists(filenya):
        await ctx.send("kh", file=discord.File(filenya))
    else:
        await ctx.send("kh")


def main():
    bot.run(config.TOKEN_BOT)
