# Copyright Modal Labs 2022

if __name__ == "__main__":
    with app.run():
        for x in f.map([1, 2, 3]):  # type: ignore
            pass
