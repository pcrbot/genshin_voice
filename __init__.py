import json
import os
import random
from typing import Optional, Tuple

from nonebot import CommandSession

import hoshino
from . import update
from hoshino import Service

language_mapping = {'汉语': 'cn', '英语': 'en', '日语': 'jp', '韩语': 'kr'}

try:
	with open(os.path.join(os.path.dirname(__file__), 'char_name.json'), 'r', encoding='utf8') as f:
		char_name = json.load(f)
	
	with open(os.path.join(os.path.dirname(__file__), 'char_voice.json'), 'r', encoding='utf8') as f:
		char_voice = json.load(f)
except Exception as e:
	hoshino.logger.error("loading file failed:", e)


def name_zh2en(name: str) -> Tuple[str, bool]:
	"""
	:return: name, exists or not
	"""
	for k, v in char_name.items():
		if name in v:
			return k, True
	return char_name["unknown"][0], False


def get_random_voice(name: Optional[str] = None, language: Optional[str] = 'cn') -> Optional[str]:
	if not name:
		characters = random.choice(list(char_voice.keys()))
		action = random.choice(list(char_voice.get(characters).keys()))
		voice = char_voice.get(characters, {}).get(action, {}).get(language)
		return voice
	else:
		characters = name_zh2en(name)
		if not characters[1]:
			return None
		characters = characters[0]
		voice = None
		i = 3
		while (not voice) or i >= 0:
			action = random.choice(list(char_voice.get(characters).keys()))
			voice = char_voice.get(characters, {}).get(action, {}).get(language)
			i -= 1
		return voice


_help = """
[原神语音 (角色名) (语言名)] 播放一段角色的语音(全部语言包括汉语、英语、日语、韩语)
[更新语音列表] 从资源站上更新语音列表
"""

sv = Service('原神语音', enable_on_default=True, help_=_help)


@sv.on_command("原神语音")
async def get_voices(session: CommandSession):
	args = session.current_arg.split()
	if not args:
		voice = None
		while not voice:
			voice = get_random_voice()
		session.finish(f'[CQ:record,file={voice}]')
	elif len(args) == 1:
		char = args[0]
		voice = get_random_voice(char)
		if not voice:
			session.finish("无法识别角色名")
		session.finish(f'[CQ:record,file={voice}]')
	elif len(args) == 2:
		char = args[0]
		language = language_mapping.get(args[1])
		if not language:
			session.finish("没有这种语言的语音")
		voice = get_random_voice(char, language)
		if not voice:
			session.finish("无法识别角色名")
		session.finish(f'[CQ:record,file={voice}]')
	else:
		session.finish("参数错误")


@sv.on_command("更新语音列表")
async def update_voices(session: CommandSession):
	await session.send("开始更新...")
	update.main()
	session.finish("更新完成")


@sv.scheduled_job('cron', hour=19)
async def update_voices_regularly():
	update.main()
