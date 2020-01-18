from randomboye import raspi
import time

pi = raspi.RaspberryPi()
pi.start()

time.sleep(2)

for i in range(10):
    print_job = ([f"Pavement       {i}", "Slanted And Ench"])
    pi.add_to_print_jobs_queue(print_job)

time.sleep(2)

for i in range(10):
    print_job = (["Pavement       {i}", "Slanted And Ench"])
    pi.add_to_print_jobs_queue(print_job)
