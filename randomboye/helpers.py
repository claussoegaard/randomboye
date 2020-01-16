# from threading import Thread
# import time


def pad(line, n=16, start=0):
    """Given a string, substrings to start,
    and right pads n spaces. Returns
    an n long string.
    """
    padding = " " * n
    line = line[start:] + padding
    line = line[:n]
    return line


def create_padded_lines(line, n=16):
    """Given a string, returns list of padded substrings
    of n length into that string. Example:
    "Slanted And Enchanted", 16 will return:
    ["Slanted And Ench", "lanted And Encha", ..., "ed And Enchanted"]
    "Pavement", 16 will just return:
    ["Pavement        "]
    """
    lines = []
    steps = max(len(line) - n, 0) + 1
    for i in range(steps):
        lines.append(pad(line, n, start=i))
    return lines


def create_framebuffers(lines, n=16):
    framebuffer_pivoted = []
    steps_of_longest_string = max([max(len(line) - n, 0) + 1 for line in lines])

    for line in lines:
        padded_lines = create_padded_lines(line, n)
        step_delta = steps_of_longest_string - len(padded_lines)
        if step_delta > 0:
            last_step_repeast = [padded_lines[-1]] * step_delta
            padded_lines.extend(last_step_repeast)
        framebuffer_pivoted.append(padded_lines)

    # Got lazy here, needed to pivot list to fit format rasperry pi expects,
    # probably some much smoother way to do this.
    framebuffers = []

    for i in range(steps_of_longest_string):
        step_list = []
        for j in range(len(lines)):
            step_list.append(framebuffer_pivoted[j][i])
        framebuffers.append(step_list)

    return framebuffers


line1 = "Slanted And"
line2 = "Pavement"
lines = [line1, line2]

framebuffers = create_framebuffers(lines)

print(framebuffers)
# [print(len(x)) for x in framebuffers]
