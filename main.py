# main.py
import cv2
import mediapipe as mp
import numpy as np
import random

# Import our custom modules
from utils import get_dist, get_dist_to_segment
from config import COLORS_PALETTE, ERASER_RADIUS, PINCH_THRESHOLD, WIPE_THRESHOLD

def main():
    # Initialize MediaPipe Hand tracking
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
    mp_draw = mp.solutions.drawing_utils

    # Start webcam
    cap = cv2.VideoCapture(0)
    
    # --- State Management ---
    # We store strokes as a dictionary containing the points, color, and brush size
    strokes = [] 
    current_stroke_pts = []
    particles = []      
    wipe_positions = [] 
    
    current_color = (0, 0, 255) # Default to Red
    active_stroke_idx = -1 
    prev_hand_pos = None

    while True:
        success, frame = cap.read()
        if not success: 
            break
            
        # Flip the frame horizontally for a natural mirror-like feel
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # We draw our UI on a separate blank canvas so we can overlay it cleanly
        ui_layer = np.zeros((h, w, 3), dtype=np.uint8)
        
        # MediaPipe needs RGB, but OpenCV uses BGR natively
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)
        
        # Reset defaults for this frame
        mode = "STANDING BY"
        is_drawing = False
        ix, iy = 0, 0 # Index finger tip coordinates

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                lm = hand_landmarks.landmark
                
                # Map normalized landmark coordinates back to screen pixels
                ix, iy = int(lm[8].x * w), int(lm[8].y * h)   # Index fingertip
                tx, ty = int(lm[4].x * w), int(lm[4].y * h)   # Thumb tip
                px, py = int(lm[9].x * w), int(lm[9].y * h)   # Palm center
                
                # Check which fingers are currently up (tips higher than lower joints)
                fingers = [lm[i].y < lm[i-2].y for i in [8, 12, 16, 20]]
                
                dist_pinch = get_dist((ix, iy), (tx, ty))
                
                # Dynamically adjust brush thickness based on how close the hand is to the camera
                hand_size = get_dist((lm[0].x*w, lm[0].y*h), (lm[9].x*w, lm[9].y*h))
                brush_thickness = int(np.interp(hand_size, [70, 180], [3, 20]))

                # -------------------------
                # GESTURE RECOGNITION LOGIC
                # -------------------------

                # 1. UI Menu Hover: Is the index finger at the very top of the screen?
                if iy < 70:
                    mode = "MENU"
                    for item in COLORS_PALETTE:
                        if item["coord"][0] < ix < item["coord"][1]:
                            if item["name"] == "CLEAR": 
                                strokes.clear()
                            else: 
                                current_color = item["color"]

                # 2. The Duster: All fingers up + rapid hand movement clears the screen
                elif all(fingers):
                    wipe_positions.append((px, py))
                    # Keep only the last 30 frames of motion
                    if len(wipe_positions) > 30: 
                        wipe_positions.pop(0)
                        
                    # Calculate total distance traveled recently
                    motion_distance = sum(get_dist(wipe_positions[k-1], wipe_positions[k]) for k in range(1, len(wipe_positions)))
                    
                    if motion_distance > WIPE_THRESHOLD:
                        strokes.clear()
                        mode = "SCREEN CLEARED"
                    else: 
                        mode = "PALM OPEN"

                # 3. The Precision Eraser: Index and middle fingers up (peace sign)
                elif fingers[0] and fingers[1] and not fingers[2]:
                    mode = "ERASER ACTIVE"
                    # Iterate through all strokes and delete the ones that intersect with the eraser
                    new_strokes = []
                    for s in strokes:
                        keep_stroke = True
                        pts = s["points"]
                        
                        # Handle dots vs lines
                        if len(pts) == 1:
                            if get_dist((ix, iy), pts[0]) < ERASER_RADIUS: 
                                keep_stroke = False
                        else:
                            # Check every segment of the drawn line
                            for i in range(len(pts)-1):
                                if get_dist_to_segment((ix, iy), pts[i], pts[i+1]) < ERASER_RADIUS:
                                    keep_stroke = False
                                    break
                                    
                        if keep_stroke:
                            new_strokes.append(s)
                    strokes = new_strokes

                # 4. Grab & Move: Pinching index and thumb to drag existing strokes around
                elif dist_pinch < PINCH_THRESHOLD:
                    mode = "GRABBING"
                    # If we haven't grabbed a stroke yet, find the closest one
                    if active_stroke_idx == -1:
                        for i, s in enumerate(strokes):
                            if any(get_dist((ix, iy), pt) < PINCH_THRESHOLD for pt in s["points"]):
                                active_stroke_idx = i
                                break
                                
                    # If we have a stroke grabbed, move all its points relative to hand movement
                    if active_stroke_idx != -1 and prev_hand_pos:
                        dx = ix - prev_hand_pos[0]
                        dy = iy - prev_hand_pos[1]
                        for pt in strokes[active_stroke_idx]["points"]:
                            pt[0] += dx
                            pt[1] += dy
                    prev_hand_pos = (ix, iy)

                # 5. Drawing: Only the index finger is up
                elif fingers[0] and not fingers[1]:
                    mode = "DRAWING"
                    is_drawing = True
                    current_stroke_pts.append([ix, iy])
                    active_stroke_idx = -1
                    prev_hand_pos = None

                # 6. Standby: Not doing any specific gesture
                else:
                    if current_stroke_pts:
                        # Noise Filter: Prevent accidental single-pixel dots from rapid hand movements
                        if len(current_stroke_pts) > 2:
                            strokes.append({"points": current_stroke_pts, "color": current_color, "thickness": brush_thickness})
                        current_stroke_pts = []
                        
                    active_stroke_idx = -1
                    prev_hand_pos = None
                    mode = "HOVERING"

                # Overlay the MediaPipe skeletal connections for visual feedback
                mp_draw.draw_landmarks(ui_layer, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # -------------------------
        # RENDERING PIPELINE
        # -------------------------
        
        # Render the color palette at the top
        for item in COLORS_PALETTE:
            cv2.rectangle(ui_layer, (item["coord"][0], 0), (item["coord"][1], 60), item["color"], -1)
            cv2.putText(ui_layer, item["name"], (item["coord"][0]+5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        # Render all finalized strokes
        for s in strokes:
            pts = np.array(s["points"], np.int32)
            cv2.polylines(ui_layer, [pts], False, s["color"], s["thickness"])

        # Render the stroke currently being drawn
        if current_stroke_pts:
            pts = np.array(current_stroke_pts, np.int32)
            cv2.polylines(ui_layer, [pts], False, current_color, 5)
        
        # Render the eraser UI ring
        if mode == "ERASER ACTIVE":
            cv2.circle(ui_layer, (ix, iy), ERASER_RADIUS, (255, 255, 255), 2) 

        # Render sparkles trailing the drawing finger
        if is_drawing:
            # Add a new particle [x, y, x_velocity, y_velocity, lifespan]
            particles.append([float(ix), float(iy), random.uniform(-3, 3), random.uniform(-3, 3), 10])
            
        for p in particles[:]:
            p[0] += p[2] # Update X
            p[1] += p[3] # Update Y
            p[4] -= 1    # Decrease lifespan
            
            if p[4] <= 0: 
                particles.remove(p)
            else: 
                cv2.circle(ui_layer, (int(p[0]), int(p[1])), 2, (255, 255, 255), -1)

        # Print current mode to the screen for debugging/user info
        cv2.putText(ui_layer, f"MODE: {mode}", (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display the final composed frame
        cv2.imshow("AirPainter CV", ui_layer)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()