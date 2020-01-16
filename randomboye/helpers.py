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


def pad_lines(line, n=16):
    """Given a string, returns list of padded substrings
    of n length into that string. Example:
    "Slanted And Enchanted", 16 will return:
    ["Slanted And Ench", "lanted And Encha", ..., "ed And Enchanted"]
    "Pavement", 16 will just return:
    ["Pavement        "]
    if last_repeats > 0, the list item of the padded lines will be repeated
    last_repeats times. So for "Pavement" with last_repeats=2, output
    will be:
    ['Pavement        ', 'Pavement        ', 'Pavement        ']
    """
    lines = []
    steps = max(len(line) - n, 0) + 1
    for i in range(steps):
        lines.append(pad(line, n, start=i))
    return lines


def create_framebuffers(lines, n=16):
    framebuffers = []
    steps_of_longest_string = max([max(len(line) - n, 0) + 1 for line in lines])

    for line in lines:
        padded_lines = pad_lines(line, n)
        step_delta = steps_of_longest_string - len(padded_lines)
        if step_delta > 0:
            last_step_repeast = [padded_lines[-1]] * step_delta
            padded_lines.extend(last_step_repeast)
        framebuffers.append(padded_lines)

    return framebuffers


# line1 = "Slanted And Enchanted"
# line2 = "Pavement"
# lines = [line1, line2]

# framebuffers = create_framebuffers(lines)

# print(framebuffers)
# [print(len(x)) for x in framebuffers]
