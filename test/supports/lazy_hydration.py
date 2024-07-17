# Copyright Modal Labs 2024
from modal import App, Image, Queue, Volume

app = App()

image = Image.debian_slim().pip_install("xyz")
volume = Volume.from_name("my-vol")
queue = Queue.from_name("my-queue")
