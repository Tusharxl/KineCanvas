# utils.py
import math

def get_dist(p1, p2):
    """Calculates the straight-line distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_dist_to_segment(p, s1, s2):
    """
    Finds the shortest distance from a point to a line segment.
    We use this specifically for the eraser tool to see if the user's finger 
    is hovering over any part of a drawn line, not just the vertices.
    """
    px, py = p
    x1, y1 = s1
    x2, y2 = s2
    dx, dy = x2 - x1, y2 - y1
    
    # If the segment is literally just a dot, return the simple distance
    if dx == 0 and dy == 0:
        return get_dist(p, s1)
    
    # Calculate the projection of the point onto the line using the dot product
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    
    # Clamp 't' to between 0 and 1 so we don't accidentally erase lines 
    # by pointing at the empty space far past the end of the segment
    t = max(0, min(1, t)) 
    
    # Find the nearest actual point on that line segment
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    
    return get_dist(p, (nearest_x, nearest_y))