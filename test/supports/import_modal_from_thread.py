# Copyright Modal Labs 2024
import threading

success = threading.Event()


def main():
    import modal  # noqa

    success.set()


if __name__ == "__main__":
    t.start()
    assert was_success
