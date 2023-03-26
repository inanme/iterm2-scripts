#!/usr/bin/env python3.10

import iterm2
import socket


# ~/Library/Application Support/iTerm2/Scripts
# socat -U TCP-LISTEN:10558,fork EXEC:'/bin/ls',stderr,pty,echo=0
def is_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', 10558))
        return True if result == 0 else False


async def main(connection):
    # Your code goes here. Here's a bit of example code that adds a tab to the current window:
    app = await iterm2.async_get_app(connection)
    window = app.current_terminal_window
    if window is not None:
        tab = await window.async_create_tab()
        command_session = tab.current_session
        await command_session.async_send_text("export HTTPS_PROXY=socks5://localhost:10558\n")
        if not is_open():
            tunnel_session = await command_session.async_split_pane(vertical=True)
            await tunnel_session.async_send_text("bws exec -- ssh -ND10558 jumpbox\n")
            # await tab.async_select_pane_in_direction(iterm2.NavigationDirection.LEFT)
    else:
        # You can view this message in the script console.
        print("No current window")


iterm2.run_until_complete(main)
