def logi(msg):
    with open("./temp/logi.log", "w") as f:
        f.write(msg)


def logi_clear():
    logi("")


def logi_append(msg):
    with open("./temp/logi.log", "a") as f:
        f.write(msg)
        f.write("\n\n")
