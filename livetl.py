from langdetect.lang_detect_exception import LangDetectException
from filter import parseTranslation
from pathlib import Path
import googletrans
import langdetect
import pafy
import pytchat as pyt
import sys
import threading
import tkinter as tk
import tkinter.scrolledtext
import tkinter.ttk
import vlc

translator = googletrans.Translator()
isClosed = False
CHAT_LANGUAGES = {'All': 'All', 'Japanese':'jp', 'English':'en', 'Bahasa Indonesia':'id', 'Chinese':'zh', 'Spanish':'es', 'Korean':'kr'}
TL_LANGUAGES = ['en','jp','es','id','kr','ch','ru','fr']

while True:
    def on_close():
        global isClosed
        isClosed = True
        raise SystemExit

    chooseVideo = tk.Tk()
    chooseVideo.iconbitmap('img/128x128.ico')
    idvar = tk.StringVar()
    chooseVideo.title("Choose Video")
    chooseVideo.geometry("400x400")
    chooseVideo.resizable(False, False)
    id_box = tk.Entry(chooseVideo, textvariable=idvar)
    id_box.pack()
    id_box.focus_set()
    id_box.bind('<Return>', lambda x: chooseVideo.destroy())
    chooseVideo.protocol("WM_DELETE_WINDOW", on_close)
    chooseVideo.mainloop()
    try_id = idvar.get()
    if try_id != '':
        try:
            id_index = try_id.index('watch?v=') + 8
            try_id = try_id[id_index:id_index + 11]
        except:
            sys.exit()

    id = try_id or Path('./lastvideo.txt').read_text()
    with open('lastvideo.txt', 'w') as f:
        f.write(id)

    url = 'https://www.youtube.com/watch?v=' + id

    instance = vlc.Instance()
    player = instance.media_player_new()

    top = tk.Tk()
    top.iconbitmap('img/128x128.ico')
    
    def change_video():
        global isClosed
        isClosed = True
        top.destroy()
        player.stop() 


    top.protocol("WM_DELETE_WINDOW", on_close)
    top.title("LiveTL")
    main_frame = tk.Frame(top)
    main_frame.configure(background='grey')
    text_frame = tk.Frame(main_frame)
    text_frame.configure(background='grey')
    selected_chat_language = tk.StringVar(top)
    selected_chat_language.set('All')
    selected_tl_language = tk.StringVar(top)
    selected_tl_language.set('en')
    is_translate_chat = tk.StringVar(top)
    is_translate_chat.set("Don't Translate Chat")
    chat_language = tk.OptionMenu(text_frame, selected_chat_language, *CHAT_LANGUAGES.keys()) 
    translate_chat = tk.OptionMenu(text_frame, is_translate_chat, 'Translate Chat', "Don't Translate chat")
    tl_language = tk.OptionMenu(text_frame, selected_tl_language, *TL_LANGUAGES)
    chat_area = tk.scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=50, height=15, font=tk.NORMAL)
    tl_area = tk.scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=50, height=15, font=tk.NORMAL)
    change_button = tk.Button(text_frame, command=change_video, text="Change Video", width=10)
    chat_language.grid(column=0, row=0, pady=5, padx=10, sticky=tk.W+tk.E)
    translate_chat.grid(column=0, row=1, pady=10, padx=10, sticky=tk.W+tk.E)
    chat_area.grid(column=0, row=2, pady=10, padx=10, sticky=tk.W+tk.E)
    tl_language.grid(column=0, row=3, pady=5, padx=10, sticky=tk.W+tk.E)
    tl_area.grid(column=0, row=4, pady=10, padx=10, sticky=tk.W+tk.E)
    change_button.grid(column=0, row=5, pady=10, padx=10)
    video_area = tk.Frame(main_frame, width=1280, height=720)
    video_area.grid(column=0, row=0, pady=10, padx=10, sticky=tk.NSEW)
    text_frame.grid(column=1, row=0, pady=10, padx=10, sticky=tk.NSEW)
    main_frame.pack(fill=tk.BOTH, expand=True)

    chat_area.tag_config('message', foreground='grey')
    tl_area.tag_config('message', foreground='grey')

    chat = pyt.create(video_id=id)

    player.set_hwnd(video_area.winfo_id())
    player.set_media(instance.media_new(pafy.new(url).getbest().url))
    player.play()

    def run_chat():
        global selected_chat_language
        while chat.is_alive():
            if not isClosed:
                for c in chat.get().sync_items():
                    if is_translate_chat.get()[0] == "D":
                        try:
                            if CHAT_LANGUAGES[selected_chat_language.get()] in (langdetect.detect(c.message), 'All'):
                                insert_in_box(chat_area, c)
                        except LangDetectException:
                            insert_in_box(chat_area, c)
                    else:
                        c.message = translator.translate(c.message, dest=CHAT_LANGUAGES[selected_chat_language.get()]).text
                        insert_in_box(chat_area, c)
                    if parseTranslation(c, selected_tl_language.get()) != None or c.author.isChatOwner or c.author.isChatModerator:
                        insert_in_box(tl_area, c)
            else:
                break

    def insert_in_box(box, c):
        if not isClosed:
            box.configure(state=tk.NORMAL)
            box.insert(tk.END, f'\n{c.author.name}：')
            box.insert(tk.END, f'{c.message}', 'message')
            box.see(tk.END)
            if int(box.index('end').split('.')[0]) - 1 > 300:
                box.delete("1.0", "2.0")
            box.configure(state=tk.DISABLED)

    x = threading.Thread(target=run_chat)
    x.start()
    isClosed = False
    top.mainloop()