from randomboye import raspi
import time

pi = raspi.RaspberryPi()
pi.start()

time.sleep(2)

print_job = (["Pavement        ", "Slanted And Ench"])

pi.add_to_print_jobs_queue(print_job)
