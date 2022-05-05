import dearpygui.dearpygui as dpg
from util import *
import os
import pytchat as pyt
os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
import mpv
import threading

dpg.create_context()
dpg.create_viewport(title="LiveTL", small_icon='128x128.ico')
dpg.setup_dearpygui()
player = mpv.MPV(ytdl=True, geometry='1280x720+100+100')

w, h, d = 1280, 720, 3

chat = None

def run_chat():
    while chat.is_alive():
        for c in chat.get().sync_items():
            dpg.set_value('chat_text', f'{c.author.name}:{c.message}\n' + dpg.get_value('chat_text'))

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


with dpg.window(tag="initial", label="Choose Stream Link", width=300):
    dpg.add_input_text(tag='url', label='stream link', on_enter=True, callback=start_video)
    dpg.add_button(tag='start', label='start', callback=start_video)

with dpg.window(tag="chat", label='Chat', width=600):
    dpg.add_input_text(tag='chat_text', label='chat', readonly=True, multiline=True, height=130)
    dpg.add_input_text(tag='chat_text_translated', label='translated chat', readonly=True, multiline=True, height=130)
    dpg.add_input_text(tag='filtered_text', label='translations', readonly=True, multiline=True, height=130)


dpg.set_item_pos('chat', [0, 100])

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
dpg.focus_item('initial')