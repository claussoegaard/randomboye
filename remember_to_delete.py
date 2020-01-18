from randomboye import raspi
import time

pi = raspi.RaspberryPi()
pi.start()

time.sleep(2)

for i in range(10):
    fb = [f"Pavement       {i}", "Slanted And Ench"]
    pi.create_framebuffer_print_job(fb)

time.sleep(2)

for i in range(10):
    fb = ["Pavement       {i}", "Slanted And Ench"]
    pi.create_framebuffer_print_job(fb)

time.sleep(2)
framebuffers = [
    ["Pavement        ", "Slanted And Ench"],
    ["Pavement        ", "lanted And Encha"],
    ["Pavement        ", "anted And Enchan"],
    ["Pavement        ", "nted And Enchant"],
    ["Pavement        ", "ted And Enchante"],
    ["Pavement        ", "ed And Enchanted"]
]

pi.print_framebuffers(framebuffers)
