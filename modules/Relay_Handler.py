import RPi.GPIO as GPIO

class RelayHandler(object):

    def __init__(self):
        self.gpio_pin = 17
        self.relay_state = 0  # open relay

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)

    def set_gpio_pin(self, p_number):

        # do clean-up on old pin
        GPIO.cleanup(self.gpio_pin)

        self.gpio_pin = p_number
        # init new pin out number
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)

    def close_relay(self):
        # relay is closing -> current can flow
        GPIO.output(self.gpio_pin, GPIO.HIGH)
        self.relay_state = 1
        print("Relay has been closed")

    def open_relay(self):
        # relay is opening -> current stops
        GPIO.output(self.gpio_pin, GPIO.LOW)
        self.relay_state = 0
        print("Relay has been opened")

    def get_relay_state(self):
        return self.relay_state

    def do_cleanup(self):
        # do cleanup on all GPIO pins
        GPIO.cleanup()
        pass
