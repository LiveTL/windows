import os
import threading

import dearpygui.dearpygui as dpg
import googletrans
import translate
import pytchat as pyt

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
import mpv
from filter import *
from util import *

translator = translate.Translator(to_lang='en')
LANGS = tuple(googletrans.LANGCODES.keys())
TL_LANGS = ['en', 'jp', 'es', 'id', 'kr', 'ch', 'ru', 'fr']

dpg.create_context()

with dpg.font_registry():
#    with dpg.font('NotoSansMono-Regular.ttf', 18) as font1:
#        dpg.add_font_range(0x0020, 0xFFFD)
    with dpg.font('unifont.ttf', 16) as default_font:
        dpg.add_font_range(0x0020, 0xFFFD)


dpg.create_viewport(title="LiveTL", small_icon='128x128.ico', height=720, width = 1280)
dpg.setup_dearpygui()
dpg.bind_font(default_font)
#dpg.show_font_manager()

player = mpv.MPV(ytdl=True, geometry='1280x720+100+100', volume='75')

w, h, d = 1280, 720, 3

chat = None

def run_chat():
    while chat.is_alive():
        for c in chat.get().sync_items():
            try: 
                if c.message:
                    dpg.set_value('chat_text', f'{c.author.name}:{c.message}\n' + dpg.get_value('chat_text'))
                    dpg.set_value('chat_text_translated', f'{c.author.name}:{translator.translate(c.message)}\n' + dpg.get_value('chat_text_translated'))
                    if parseTranslation(c, dpg.get_value('translation_filter_language')):
                        dpg.set_value('filtered_text', f'{c.author.name}:{parseTranslation(c, dpg.get_value("translation_filter_language"))[1]}\n' + dpg.get_value('filtered_text'))
            except Exception as e:
                print(e)

chat_thread = threading.Thread(target=run_chat)

def start_video():
    global chat
    print(dpg.get_value('url'))
    player.play(dpg.get_value('url'))
    chat = pyt.LiveChat(video_id=get_ytid_from_url(dpg.get_value('url')), interruptable=False)
    print('played')
    player.wait_until_playing()
    print('playing')
    chat_thread.start()
    print('chat started')

def set_volume():
    player.volume = dpg.get_value('volume')

def set_language():
    global translator
    print('language set')
    translator = translate.Translator(to_lang = googletrans.LANGCODES[dpg.get_value('translated_chat_language')])

with dpg.window(tag="initial", label="choose stream link", width=500, no_move=True, no_collapse=True, no_close=True):
    dpg.add_input_text(tag='url', label='stream link', on_enter=True, callback=start_video)
    dpg.add_button(tag='start', label='start', callback=start_video)

with dpg.window(tag="chat", label='chat', width=800, no_move=True, no_collapse=True, no_close=True):
    dpg.add_input_text(tag='chat_text', label='chat', readonly=True, multiline=True, height=130)
    dpg.add_combo(tag='translated_chat_language', label='translated chat language', items=LANGS, default_value='english', callback=set_language)
    dpg.add_input_text(tag='chat_text_translated', label='translated chat', readonly=True, multiline=True, height=130)
    dpg.add_combo(tag='translation_filter_language', label='translation filter language', items=TL_LANGS, default_value='en')
    dpg.add_input_text(tag='filtered_text', label='translations', readonly=True, multiline=True, height=130)

with dpg.window(tag='playback', label='playback', width=300, no_move=True, no_collapse=True, no_close=True):
    dpg.add_slider_int(tag='volume', label='volume', min_value=0, max_value=100, default_value=75, callback=set_volume)


dpg.set_item_pos('chat', [0, 100])
dpg.set_item_pos('playback', [500, 0])

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
dpg.focus_item('initial')