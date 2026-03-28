import math
from hackarena3 import BotContext, DriveGear, GearShift, RaceSnapshot, run_bot, TireType

class OptimizedBot:
    def __init__(self) -> None:
        self.tick_count = 0
        self.prev_steer = 0.0
        self.prev_pos = (0.0, 0.0)
        self.vel_x = 0.0
        self.vel_z = 0.0

    def get_pos(self, p):
        """Ultra-robust position extractor."""
        if p is None: return None, None
        # Try position object
        pos = getattr(p, 'position', None)
        if pos is not None:
            x, z = getattr(pos, 'x', None), getattr(pos, 'z', None)
            if x is not None and z is not None: return float(x), float(z)
        # Try direct x,z
        x, z = getattr(p, 'x', None), getattr(p, 'z', None)
        if x is not None and z is not None: return float(x), float(z)
        # Try list
        try: return float(p[0]), float(p[2] if len(p) > 2 else p[1])
        except: return None, None

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:
        try:
            self.tick_count += 1
            car = snapshot.car
            centerline = ctx.track.centerline
            num_points = len(centerline)
            
            # 1. GET CURRENT POSITION
            cx, cz = self.get_pos(car)
            if cx is None: return

            # 2. CALCULATE VELOCITY MANUALLY (Fix for 'no attribute velocity')
            if self.tick_count > 1:
                self.vel_x = (cx - self.prev_pos[0]) * 30 # 30Hz
                self.vel_z = (cz - self.prev_pos[1]) * 30
            self.prev_pos = (cx, cz)

            # 3. STARTUP (First 50 ticks)
            if self.tick_count < 50:
                gear = GearShift.UPSHIFT if car.gear == DriveGear.NEUTRAL else GearShift.NONE
                ctx.set_controls(throttle=0.3, brake=0, steer=0, gear_shift=gear)
                return

            # 4. POSITION PREDICTION (Compensate for Lag)
            # Project 0.5 seconds ahead
            px = cx + self.vel_x * 0.5
            pz = cz + self.vel_z * 0.5

            # 5. FIND PREDICTED POSITION ON TRACK
            min_dist_sq = float('inf')
            closest_idx = 0
            for i in range(num_points):
                tx, tz = self.get_pos(centerline[i])
                if tx is None: continue
                dist_sq = (tx - px)**2 + (tz - pz)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_idx = i
            
            # 6. TARGETING (Look 3 points ahead)
            target_idx = (closest_idx + 3) % num_points
            tx, tz = self.get_pos(centerline[target_idx])

            # 7. STEERING LOGIC
            dx, dz = tx - px, tz - pz
            
            # Heading vector (hx, hz)
            if (self.vel_x**2 + self.vel_z**2) > 1.0:
                hx, hz = self.vel_x, self.vel_z
            else:
                p1x, p1z = self.get_pos(centerline[closest_idx])
                p2x, p2z = self.get_pos(centerline[(closest_idx + 1) % num_points])
                hx, hz = p2x - p1x, p2z - p1z
            
            mag_h = math.sqrt(hx**2 + hz**2)
            local_x = (dx * hz - dz * hx) / mag_h if mag_h > 0 else 0
            
            # Steering with smoothing
            target_steer = -local_x * 0.15
            target_steer = max(-1.0, min(1.0, target_steer))
            
            steer_diff = target_steer - self.prev_steer
            steer = self.prev_steer + max(-0.15, min(0.15, steer_diff))
            self.prev_steer = steer

            # 8. SPEED CONTROL (Target 50 km/h)
            target_speed = 50
            if abs(local_x) > 2.0: target_speed = 30
            
            throttle = 0.4 if car.speed_kmh < target_speed else 0.0
            brake = 0.5 if car.speed_kmh > target_speed + 5 else 0.0

            # 9. GEAR SHIFTING (Robust)
            gear_shift = GearShift.NONE
            rpm = getattr(car, 'engine_rpm', 0)
            if car.gear == DriveGear.NEUTRAL:
                gear_shift = GearShift.UPSHIFT
            elif rpm > 6500:
                gear_shift = GearShift.UPSHIFT
            elif car.speed_kmh < 15 and car.gear != DriveGear.FIRST:
                gear_shift = GearShift.DOWNSHIFT

            # 10. DIAGNOSTICS
            if self.tick_count % 20 == 0:
                print(f"SPD: {car.speed_kmh:.0f} | GEAR: {car.gear} | LX: {local_x:.1f} | STR: {steer:.2f}")

            ctx.set_controls(throttle=throttle, brake=brake, steer=steer, gear_shift=gear_shift)

        except Exception as e:
            if self.tick_count % 50 == 0: print(f"BOT ERROR: {e}")

if __name__ == "__main__":
    run_bot(OptimizedBot())
