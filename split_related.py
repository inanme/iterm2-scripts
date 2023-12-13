#!/usr/bin/env python3.10

import iterm2
import pathlib
import tempfile
import unittest


# seems like pick an interpreter here ~/Library/Application Support/iTerm2, e.g: iterm2env-3.10
# ~/Library/Application Support/iTerm2/Scripts


async def first_line(session):
    async with session.get_screen_streamer(want_contents=True) as streamer:
        while True:
            content = await streamer.async_get()
            debug = "debug=1" in session.name  # cmd + i
            if debug:
                print(content.number_of_lines)
                for line in range(content.number_of_lines):
                    print(content.line(line).string)
            return content.line(0).string


suffixes = ["us-east-1", "us-east-2", "us-west-2", "eu-central-1", "eu-west-1"]


def relative_paths(pwd: str) -> set[str]:
    if not pwd.strip():
        return set()
    pwd_path = pathlib.Path(pwd)
    parent_path = pwd_path.parent
    parent = parent_path.as_posix()
    grandparent_path = pwd_path.parent.parent
    current_folder = pwd_path.name
    key_s = parent_path.as_posix()
    for suffix in suffixes:
        key_s = key_s.removesuffix(suffix)
    return {(f / current_folder).as_posix()
            for f in grandparent_path.iterdir()
            if f.is_dir() and f.as_posix().startswith(key_s) and not f.as_posix() == parent}


async def main(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_terminal_window
    if window is not None:
        tab = window.current_tab
        command_session = tab.current_session
        await command_session.async_send_text("clear;pwd\n")
        pwd_s = await first_line(command_session)
        files = relative_paths(pwd_s)
        for file in files:
            next_session = await command_session.async_split_pane(vertical=False)
            await next_session.async_send_text(f"cd {file}\n")
    else:
        # You can view this message in the script console.
        print("No current window")  # scripts > manage > console


if __name__ == '__main__':
    iterm2.run_until_complete(main)


class Tests(unittest.TestCase):
    def test_relative_paths_empty(self):
        self.assertEqual(relative_paths(""), set())

    def test_relative_paths(self):
        folder_name = "aaa"
        with tempfile.TemporaryDirectory() as tmp_dirname:
            for suffix in suffixes:
                pathlib.Path(tmp_dirname + f"/k8c/cp2-main-{suffix}/{folder_name}").mkdir(
                    parents=True, exist_ok=True)

            current_folder = tmp_dirname + f"/k8c/cp2-main-{suffixes[0]}/{folder_name}"
            expected_relative_paths = {tmp_dirname + f"/k8c/cp2-main-{suffix}/{folder_name}" for suffix in
                                       suffixes[1::]}
            self.assertEqual(relative_paths(current_folder), expected_relative_paths)
