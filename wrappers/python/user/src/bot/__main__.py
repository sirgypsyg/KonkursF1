from hackarena3 import BotContext, DriveGear, GearShift, RaceSnapshot, TireType, run_bot


class MyBot:
    def __init__(self) -> None:
        self.tick = 0

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:
        self.tick += 1

        # Prosta logika - jazda do przodu
        throttle = 0.6
        brake = 0.0
        steer = 0.0

        # Przykladowa logika sterowania
        ctx.set_controls(
            throttle=throttle,
            brake=brake,
            steer=steer,
        )


if __name__ == "__main__":
    raise SystemExit(run_bot(MyBot()))
