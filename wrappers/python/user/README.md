import math
from hackarena3 import BotContext, DriveGear, GearShift, RaceSnapshot, run_bot, TireType

class OptimizedBot:
    def __init__(self) -> None:
        self.prev_pos = None

    def get_pos(self, p):
        # Extremely robust position getter
        if hasattr(p, 'x'): return p.x, p.y
        if hasattr(p, 'position'): return p.position.x, p.position.y
        return 0.0, 0.0

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:
        try:
            car = snapshot.car
            centerline = ctx.track.centerline
            num_points = len(centerline)

            # 1. STARTUP PHASE (First 15 ticks)
            # Just drive straight slowly to establish a heading
            if snapshot.tick < 15:
                gear = GearShift.UPSHIFT if car.gear == DriveGear.NEUTRAL else GearShift.NONE
                ctx.set_controls(throttle=0.2, brake=0, steer=0, gear_shift=gear)
                self.prev_pos = car.position
                return

            # 2. FIND POSITION (Full Track Scan)
            # We check every point to be 100% sure we are on track
            min_dist = float('inf')
            closest_idx = 0
            for i in range(num_points):
                px, py = self.get_pos(centerline[i])
                dist = (px - car.position.x)**2 + (py - car.position.y)**2
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = i

            # 3. TARGETING (20 points ahead)
            target_idx = (closest_idx + 20) % num_points
            tx, ty = self.get_pos(centerline[target_idx])

            # 4. HEADING CALCULATION
            # Where we want to go
            dx = tx - car.position.x
            dy = ty - car.position.y
            target_angle = math.atan2(dy, dx)

            # Where we are currently facing (based on movement)
            if self.prev_pos:
                vx = car.position.x - self.prev_pos.x
                vy = car.position.y - self.prev_pos.y
                # Only update if moving fast enough to be sure
                if math.sqrt(vx**2 + vy**2) > 0.01:
                    current_angle = math.atan2(vy, vx)
                else:
                    # Fallback to track direction if stationary
                    p1 = self.get_pos(centerline[closest_idx])
                    p2 = self.get_pos(centerline[(closest_idx + 1) % num_points])
                    current_angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            else:
                current_angle = target_angle

            self.prev_pos = car.position

            # 5. STEERING (Very gentle)
            error = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
            steer = max(-1.0, min(1.0, error * 0.7))

            # 6. SPEED CONTROL (Safe limit: 50 km/h)
            target_speed = 50
            throttle = 0.0
            brake = 0.0

            if car.speed_kmh < target_speed:
                throttle = 0.3 # Gentle gas
            elif car.speed_kmh > target_speed + 5:
                brake = 0.2 # Gentle brake

            # 7. GEARS
            gear_shift = GearShift.NONE
            if car.gear == DriveGear.NEUTRAL:
                gear_shift = GearShift.UPSHIFT

            # 8. EMERGENCY RESET
            # If we are way off track (30m+), request reset
            if min_dist > 30.0**2:
                ctx.request_back_to_track()
                return

            # 9. EXECUTE
            ctx.set_controls(
                throttle=throttle,
                brake=brake,
                steer=steer,
                gear_shift=gear_shift
            )

        except Exception as e:
            print(f"CRITICAL TICK ERROR: {e}")

if __name__ == "__main__":
    run_bot(OptimizedBot())
