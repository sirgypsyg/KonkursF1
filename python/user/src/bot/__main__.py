from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from hackarena3 import BotContext, DriveGear, GearShift, RaceSnapshot, run_bot
import math
import json


class StrategyAnalyzer:
    """Analizuje zachowanie bolidu i dostosowuje parametry na bieżąco"""
    
    def __init__(self):
        # Metryki średnie ( Moving average)
        self.avg_speed = 0.0
        self.avg_slip = 0.0
        self.avg_dist_from_center = 0.0
        
        # Liczniki i flagi problemów
        self.high_slip_counter = 0
        self.off_track_counter = 0
        self.slow_counter = 0
        
        # Aktualne parametry (będą dostosowywane)
        self.steer_gain = 2.5
        self.aggression = 1.0  # 0.5 = ostrożny, 1.0 = normalny, 1.5 = agresywny
        
        # Historia dla wykrywania okrążeń
        self.lap_start_idx = 0
        self.last_lap_time = 0
        self.best_lap_time = float('inf')
        
        # Debug
        self.debug_info = {}
        
    def update(self, car, centerline, closest_idx):
        speed = car.speed_mps
        slip = max(car.tire_slip.front_left, car.tire_slip.front_right,
                   car.tire_slip.rear_left, car.tire_slip.rear_right)
        
        # Odległość od centerline
        point = centerline[closest_idx]
        dist_from_center = math.sqrt(
            (car.position.x - point.position.x)**2 +
            (car.position.z - point.position.z)**2
        )
        
        # Moving average (alpha = 0.1)
        alpha = 0.1
        self.avg_speed = self.avg_speed * (1-alpha) + speed * alpha
        self.avg_slip = self.avg_slip * (1-alpha) + slip * alpha
        self.avg_dist_from_center = self.avg_dist_from_center * (1-alpha) + dist_from_center * alpha
        
        # Wykrywanie problemów
        self._detect_problems(speed, slip, dist_from_center, point)
        
        # Dostosuj parametry
        self._adjust_parameters()
        
        # Debug info
        self.debug_info = {
            'avg_speed': self.avg_speed,
            'avg_slip': self.avg_slip,
            'avg_dist': self.avg_dist_from_center,
            'steer_gain': self.steer_gain,
            'aggression': self.aggression,
            'high_slip': self.high_slip_counter,
            'off_track': self.off_track_counter,
        }
        
    def _detect_problems(self, speed, slip, dist_from_center, point):
        """Wykrywa problemy i odpowiednio reaguje"""
        
        # Problem 1: Zbyt duży poślizg
        if slip > 0.6:
            self.high_slip_counter += 1
        else:
            self.high_slip_counter = max(0, self.high_slip_counter - 1)
            
        # Problem 2: Zjeżdżanie z toru
        track_width = (point.left_width_m + point.right_width_m) / 2
        if dist_from_center > track_width * 0.8:
            self.off_track_counter += 1
        else:
            self.off_track_counter = max(0, self.off_track_counter - 1)
            
        # Problem 3: Zbyt wolno
        if speed < 5.0:
            self.slow_counter += 1
        else:
            self.slow_counter = max(0, self.slow_counter - 1)
            
    def _adjust_parameters(self):
        """Dostosowuje parametry na podstawie wykrytych problemów"""
        
        # Jeśli duży poślizg - zmniejsz agresję i wzmocnij kontrolę
        if self.high_slip_counter > 10:
            self.aggression = max(0.3, self.aggression - 0.1)
            self.steer_gain = min(4.0, self.steer_gain + 0.2)
            
        # Jeśli zjeżdża z toru - zmniejsz steer gain (mniej agresywnie)
        if self.off_track_counter > 5:
            self.steer_gain = max(1.5, self.steer_gain - 0.3)
            
        # Jeśli jedzie za wolno - zwiększ agresję (więcej gazu)
        if self.slow_counter > 20:
            self.aggression = min(1.5, self.aggression + 0.1)
            
        # Powol powrót do normy gdy wszystko OK
        if self.high_slip_counter == 0 and self.off_track_counter == 0:
            self.aggression = min(1.0, self.aggression + 0.01)
            self.steer_gain = min(2.5, self.steer_gain + 0.01)
            
    def get_throttle_multiplier(self):
        """Zwraca mnożnik throttle na podstawie agresji"""
        return 0.5 + (self.aggression * 0.5)  # 0.75 do 1.0
        
    def get_brake_multiplier(self):
        """Zwraca mnożnik hamowania na podstawie problemów"""
        if self.high_slip_counter > 5:
            return 1.2  # Hamuj mocniej przy poślizgu (ale nie za dużo)
        return 1.0


class FastBot:
    def __init__(self):
        self.last_closest_idx = 0
        self.break_points = []
        self.apex_points = []
        
        # Detekcja zablokowania
        self.stuck_counter = 0
        self.stuck_threshold = 150
        
        # ANALIZATOR STRATEGII
        self.strategy = StrategyAnalyzer()

    def analyze_track(self, centerline):
        n = len(centerline)
        
        in_turn = False
        max_curv_idx = 0
        max_curv = 0
        
        for i in range(n):
            curv = abs(centerline[i].curvature_1pm)
            
            if curv > 0.03 and not in_turn:
                in_turn = True
                max_curv = curv
                max_curv_idx = i
            elif curv > 0.03 and in_turn:
                if curv > max_curv:
                    max_curv = curv
                    max_curv_idx = i
            elif curv <= 0.02 and in_turn:
                in_turn = False
                brake_idx = max(0, max_curv_idx - 15)
                self.break_points.append(brake_idx)
                self.apex_points.append(max_curv_idx)
        
        print(f"Znaleziono {len(self.break_points)} zakretow")

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:
        if not self.break_points:
            self.analyze_track(ctx.track.centerline)
        
        car = snapshot.car
        car_pos = car.position
        centerline = ctx.track.centerline
        n = len(centerline)

        # Znajdź najbliższy punkt
        min_dist = float('inf')
        closest_idx = self.last_closest_idx
        
        for offset in range(-100, 100):
            idx = (self.last_closest_idx + offset) % n
            point = centerline[idx]
            dist = math.sqrt(
                (point.position.x - car_pos.x)**2 +
                (point.position.z - car_pos.z)**2
            )
            if dist < min_dist:
                min_dist = dist
                closest_idx = idx
        
        self.last_closest_idx = closest_idx
        
        # === AKTUALIZUJ ANALIZATOR STRATEGII ===
        self.strategy.update(car, centerline, closest_idx)

        speed = car.speed_mps
        brake = 0.0
        throttle = 1.0
        
        # Szukaj brake pointa
        for i, bp in enumerate(self.break_points):
            dist_to_bp = (bp - closest_idx) % n
            
            if 1 <= dist_to_bp <= 10:
                curv = abs(centerline[self.apex_points[i]].curvature_1pm)
                
                base_brake = 0.0
                if curv > 0.08:
                    base_brake = 0.9
                elif curv > 0.05:
                    base_brake = 0.8
                else:
                    base_brake = 0.7
                    
                brake = min(1.0, base_brake * self.strategy.get_brake_multiplier())
                throttle = 0.0
                break
        
        # Lookahead
        lookahead = 3
        target_idx = (closest_idx + lookahead) % n
        target = centerline[target_idx]

        dx = target.position.x - car_pos.x
        dz = target.position.z - car_pos.z
        target_angle = math.atan2(dx, dz)

        q = car.orientation
        car_yaw = math.atan2(2 * (q.w * q.y + q.x * q.z), 1 - 2 * (q.y * q.y + q.z * q.z))

        angle_error = target_angle - car_yaw
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi

        # Użyj steer gain z analizatora
        target_steer = -angle_error * self.strategy.steer_gain
        target_steer = max(-1.0, min(1.0, target_steer))

        steer = target_steer

        # Zwykłe hamowanie (bez brake point)
        if brake == 0.0:
            slip = car.tire_slip
            max_slip = max(slip.front_left, slip.front_right, slip.rear_left, slip.rear_right)
            curvature = abs(centerline[target_idx].curvature_1pm)
            
            throttle_mult = self.strategy.get_throttle_multiplier()

            if curvature > 0.08:
                throttle = 0.45 * throttle_mult
            elif curvature > 0.05:
                throttle = 0.6 * throttle_mult
            elif curvature > 0.03:
                throttle = 0.8 * throttle_mult

            if max_slip > 0.8:
                throttle = 0.3 * throttle_mult
            elif max_slip > 0.6:
                throttle = max(throttle, 0.5 * throttle_mult)

        # Gear shifting
        rpm = car.engine_rpm
        gear = car.gear
        
        if gear == DriveGear.NEUTRAL or gear == DriveGear.REVERSE:
            gear_shift = GearShift.UPSHIFT
        elif rpm > 12500 and gear.value < 8:
            gear_shift = GearShift.UPSHIFT
        elif rpm < 4000 and gear.value > 1:
            gear_shift = GearShift.DOWNSHIFT
        else:
            gear_shift = GearShift.NONE

        # Reset gdy stoi
        if speed < 1.0:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        
        if self.stuck_counter > self.stuck_threshold:
            if snapshot.car.command_cooldowns.back_to_track_remaining_ms == 0:
                ctx.request_back_to_track()
                self.stuck_counter = 0

        # Debug output co 60 ticków
        if snapshot.tick % 60 == 0:
            d = self.strategy.debug_info
            print(f"[{snapshot.tick}] speed:{d['avg_speed']:.1f} slip:{d['avg_slip']:.2f} "
                  f"gain:{d['steer_gain']:.2f} agg:{d['aggression']:.2f}")

        ctx.set_controls(
            throttle=throttle,
            brake=brake,
            steer=steer,
            gear_shift=gear_shift,
        )


if __name__ == "__main__":
    raise SystemExit(run_bot(FastBot()))
