from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from hackarena3 import BotContext, DriveGear, GearShift, RaceSnapshot, run_bot
import math
import json


class TrackVisualizer:
    def __init__(self):
        self.last_closest_idx = 0
        self.track_data = None
        self.tick_count = 0

    def analyze_and_save(self, centerline):
        n = len(centerline)
        
        points = []
        break_points = []
        apex_points = []
        turn_regions = []
        
        in_turn = False
        turn_start = 0
        max_curv_idx = 0
        max_curv = 0
        
        for i in range(n):
            point = centerline[i]
            curv = abs(point.curvature_1pm)
            
            points.append({
                'idx': i,
                'x': point.position.x,
                'z': point.position.z,
                'curvature': curv,
                's_m': point.s_m,
                'left_width': point.left_width_m,
                'right_width': point.right_width_m,
            })
            
            if curv > 0.03 and not in_turn:
                in_turn = True
                turn_start = i
                max_curv = curv
                max_curv_idx = i
            elif curv > 0.03 and in_turn:
                if curv > max_curv:
                    max_curv = curv
                    max_curv_idx = i
            elif curv <= 0.02 and in_turn:
                in_turn = False
                brake_idx = max(0, max_curv_idx - 15)
                break_points.append({
                    'idx': brake_idx,
                    'x': centerline[brake_idx].position.x,
                    'z': centerline[brake_idx].position.z,
                    'curvature': max_curv
                })
                apex_points.append({
                    'idx': max_curv_idx,
                    'x': centerline[max_curv_idx].position.x,
                    'z': centerline[max_curv_idx].position.z,
                    'curvature': max_curv
                })
                turn_regions.append({
                    'start': turn_start,
                    'apex': max_curv_idx,
                    'end': i,
                    'curvature': max_curv
                })
        
        data = {
            'map_id': 'unknown',
            'lap_length_m': centerline[-1].s_m if centerline else 0,
            'total_points': n,
            'points': points,
            'break_points': break_points,
            'apex_points': apex_points,
            'turn_regions': turn_regions,
        }
        
        with open('track_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Zapisano {n} punktow")
        print(f"Znaleziono {len(turn_regions)} zakretow")
        
        return data

    def on_tick(self, snapshot: RaceSnapshot, ctx: BotContext) -> None:
        self.tick_count += 1
        
        # Analizuj tor raz na początku
        if self.track_data is None:
            self.track_data = self.analyze_and_save(ctx.track.centerline)
        
        # Znajdź najbliższy punkt centerline
        car = snapshot.car
        car_pos = car.position
        centerline = ctx.track.centerline
        n = len(centerline)
        
        min_dist = float('inf')
        closest_idx = self.last_closest_idx
        
        for offset in range(-50, 50):
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
        
        # Zapisz pozycję bolidu co 5 ticków (żeby nie spowalniać)
        if self.tick_count % 5 == 0:
            car_data = {
                'tick': self.tick_count,
                'x': car_pos.x,
                'z': car_pos.z,
                'speed': car.speed_mps,
                'rpm': car.engine_rpm,
                'gear': str(car.gear),
                'closest_idx': closest_idx,
                'curvature': abs(centerline[closest_idx].curvature_1pm),
            }
            
            with open('car_position.json', 'w') as f:
                json.dump(car_data, f)
        
        ctx.set_controls(throttle=0, brake=0, steer=0)


if __name__ == "__main__":
    raise SystemExit(run_bot(TrackVisualizer()))
