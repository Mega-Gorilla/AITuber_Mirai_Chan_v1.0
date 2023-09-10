color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}
def print_color(text, color="red",end=False):
    if end:
        print(color_dic[color] + text + color_dic["end"],end='')
    else:
        print(color_dic[color] + text + color_dic["end"])