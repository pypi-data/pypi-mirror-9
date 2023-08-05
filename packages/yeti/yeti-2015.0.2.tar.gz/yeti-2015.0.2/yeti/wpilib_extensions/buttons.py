import asyncio

class Button:

    def __init__(self, joystick, button):
        self.joystick = joystick
        self.button = button

    @asyncio.coroutine
    def until_rising(self):
        last_val = True
        while True:
            val = self.joystick.getRawButton(self.button)
            if val and not last_val:
                return
            last_val = val
            yield from asyncio.sleep(.02)

    @asyncio.coroutine
    def until_falling(self):
        last_val = False
        while True:
            val = self.joystick.getRawButton(self.button)
            if not val and last_val:
                return
            last_val = val
            yield from asyncio.sleep(.02)

    @asyncio.coroutine
    def until_pressed(self):
        while not self.joystick.getRawButton(self.button):
            yield from asyncio.sleep(.02)