import RPi.GPIO as GPIO


class RelayHandler(object):

    def __init__(self):
        self.gpio_pin = 17
        self._relay_state = 0  # 0 = open relay, 1 = close relay

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)

    def set_gpio_pin(self, p_number):

        # do clean-up on old pin
        GPIO.cleanup(self.gpio_pin)

        self.gpio_pin = p_number
        # init new pin out number
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)
        self._relay_state = 0

    def close_relay(self):
        # relay is closing -> current can flow
        if self._relay_state is 0:
            GPIO.output(self.gpio_pin, GPIO.HIGH)
            self._relay_state = 1
            print("Relay has been closed")

    def open_relay(self):
        # relay is opening -> current stops
        if self._relay_state is 1:
            GPIO.output(self.gpio_pin, GPIO.LOW)
            self._relay_state = 0
            print("Relay has been opened")

    def get_relay_state(self):
        return self._relay_state

    def do_cleanup(self):
        # do cleanup on all GPIO pins
        GPIO.cleanup()
