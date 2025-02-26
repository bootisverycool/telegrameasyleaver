from telethon.sync import TelegramClient
import configparser
import tkinter as tk
from tkinter import ttk

config = configparser.ConfigParser()
config.read("config.ini")

def get_config(section):
    config_data = {}
    options = config.options(section)
    for option in options:
        try:
            value = config.get(section, option)
            if value != -1:
                config_data[option] = value
        except Exception:
            print(f"Error processing option: {option}")
            config_data[option] = None
    return config_data


client = TelegramClient('session_name', get_config("Config")['apiId'], get_config("Config")['apiHash'])


def display_delete_gui(channels, users, groups):
    def on_delete():
        selected_ids = [item["id"] for item in channels + users + groups if var_dict.get(item["id"]) and var_dict[item["id"]].get()]
        root.selected_items = selected_ids
        root.quit()

    root = tk.Tk()
    root.title("Telegram Easy Leaver by boot :D")
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    data_dict = {"Channels": channels, "Users": users, "Groups": groups}
    var_dict = {}

    def create_tab(parent, data_list):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind("<MouseWheel>", on_mouse_wheel)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        select_all_var = tk.IntVar()

        def toggle_all():
            state = select_all_var.get()
            for item in data_list:
                var_dict[item["id"]].set(state)

        ttk.Checkbutton(scrollable_frame, text="Select All", variable=select_all_var, command=toggle_all).pack(anchor="w")

        for item in data_list:
            if item["id"] not in var_dict:
                var_dict[item["id"]] = tk.IntVar(value=0)
            ttk.Checkbutton(scrollable_frame, text=f'{item["title"]} (ID: {item["id"]})', variable=var_dict[item["id"]]).pack(anchor="w")

        return frame

    for name, data in data_dict.items():
        notebook.add(create_tab(notebook, data), text=f'{name} ({len(data)})')

    ttk.Button(root, text="Delete", command=on_delete).pack(pady=10)
    root.selected_items = []
    root.mainloop()

    return root.selected_items


async def main():
    groups, channels, users = [], [], []

    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            channels.append({'title': dialog.title, 'id': dialog.id, 'type': 'channel'})
        elif dialog.is_group and dialog.title not in [group['title'] for group in groups]:
            groups.append({'title': dialog.title, 'id': dialog.id, 'type': 'group'})
        elif dialog.is_user:
            users.append({'title': dialog.title, 'id': dialog.id, 'type': 'user'})

    items_to_delete = list(set(display_delete_gui(channels, users, groups)))

    async for dialog in client.iter_dialogs():
        if dialog.id in items_to_delete:
            print(f'Deleting {dialog.name} (ID: {dialog.id})')
            if dialog.is_user:
                async for message in client.iter_messages(dialog.id):
                    await client.delete_messages(dialog.id, message)
                await dialog.delete(revoke=True)
            else:
                await dialog.delete(revoke=True)


with client:
    client.loop.run_until_complete(main())
