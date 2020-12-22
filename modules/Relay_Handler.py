# import RPI.GPIO as GPIO

class RelayHandler(object):

    def __init__(self):
        self.gpio_pin = 11

        # GPIO.setup(self.gpio_pin, GPIO.out, initial=GPIO.LOW)

    def set_gpio_pin(self, p_number):

        # do clean-up on old pin
        # GPIO.cleanup(self.gpio_pin)

        self.gpio_pin = p_number
        # init new pin out number
        # GPIO.setup(self.gpio_pin, GPIO.out, initial=GPIO.LOW)

    def close_relay(self):
        # relay is closing -> current can flow
        # GPIO.output(self.gpio_pin, GPIO.HIGH)
        print("Relay has been closed")

    def open_relay(self):
        # relay is opening -> current stops
        # GPIO.output(self.gpio_pin, GPIO.LOW)
        print("Relay has been opened")

    def do_cleanup(self):
        # do cleanup on all GPIO pins
        # GPIO.cleanup()
        pass
