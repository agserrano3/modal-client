# Copyright Modal Labs 2022
import pytest

import modal

assert threading.current_thread() == threading.main_thread()

app = modal.App()
