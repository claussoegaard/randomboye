from definitions import FUNCTION_CALL_MSG
from logs.config import logger
logger = logger(__name__)


def pad(line, n=16, start=0):
    """Given a string, substrings to start,
    and right pads n spaces. Returns
    an n long string.
    """
    logger.debug(FUNCTION_CALL_MSG)
    padding = " " * n
    line = line[start:] + padding
    line = line[:n]
    return line


def framebuffer_line_steps(line, n=16):
    """Returns how many framebuffer steps
    a given line will have, in an n-wide framebuffer.
    Example:
    "Slanted And Enchanted" and n==16 will
    return 6. "Pavement" will return 1.
    """
    logger.debug(FUNCTION_CALL_MSG)
    return max(len(line) - n, 0) + 1


def create_framebuffers(lines, n=16):
    """Creates a list of framebuffers required
    to scroll through the longest of lines, end
    to end.
    Example:
    ['Pavement', 'Slanted And Enchanted'] will return
    the below for n==16
    ['Pavement        ', 'Slanted And Ench']
    ['Pavement        ', 'lanted And Encha']
    ['Pavement        ', 'anted And Enchan']
    ['Pavement        ', 'nted And Enchant']
    ['Pavement        ', 'ted And Enchante']
    ['Pavement        ', 'ed And Enchanted']
    """
    logger.debug(FUNCTION_CALL_MSG)
    steps_of_longest_string = max([framebuffer_line_steps(line, n) for line in lines])
    framebuffers = []
    for i in range(steps_of_longest_string):
        framebuffer_for_step = []
        for line in lines:
            line_step = min(framebuffer_line_steps(line, n) - 1, i)
            framebuffer_for_step.append(pad(line=line, n=n, start=line_step))
        framebuffers.append(framebuffer_for_step)
    return framebuffers


def create_multiple_framebuffers(lines_of_lines, n=16):
    """Just calls create_framebuffers for each item
    in lines_of_lines.
    """
    logger.debug(FUNCTION_CALL_MSG)
    multiple_framebuffers = []
    for lines in lines_of_lines:
        multiple_framebuffers.append(create_framebuffers(lines, n))
    return multiple_framebuffers
