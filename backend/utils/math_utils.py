import numpy as np 


def magnitude(vector: np.ndarray) -> float:
    return np.linalg.norm(vector)

def normalize(vector: np.ndarray) -> np.ndarray:
    mag = magnitude(vector)
    if mag == 0:
        return np.array([0.0, 0.0])
    return vector / mag

def rotate_vector(vector: np.ndarray, angle: float) -> np.ndarray:
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    x, y = vector
    return np.array([x * cos_a - y * sin_a, x * sin_a + y * cos_a])

def angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    dot = np.dot(v1, v2)
    mags = magnitude(v1) * magnitude(v2)
    if mags == 0:
        return 0.0
    return np.arccos(np.clip(dot / mags, -1.0, 1.0))

def line_intersection(
    p1: np.ndarray, 
    p2: np.ndarray,
    p3: np.ndarray,
    p4: np.ndarray
) -> tuple[np.ndarray, float, float] | None:
    d1 = p2 - p1
    d2 = p4 - p3
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-10:
        return None
    dp = p3 - p1
    t = (dp[0] * d2[1] - dp[1] * d2[0]) / cross
    u = (dp[0] * d1[1] - dp[1] * d1[0]) / cross

    if 0 <= t <= 1 and 0 <= u <= 1:
        intersection = p1 + t * d1
        return intersection, t, u
    return None

def batch_line_intersection(
    p1: np.ndarray, 
    p2: np.ndarray,
    p3: np.ndarray,
    p4: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes batched line segment intersections.
    p1, p2: shape (N, 2) or broadcastable (N, 1, 2)
    p3, p4: shape (M, 2) or broadcastable (1, M, 2)
    Returns:
        t: array of intersection point distances along p1->p2
        valid: boolean mask where True means segments intersect
    """
    d1 = p2 - p1
    d2 = p4 - p3
    
    # Cross product
    cross = d1[..., 0] * d2[..., 1] - d1[..., 1] * d2[..., 0]
    
    dp = p3 - p1
    
    # Temporarily ignore division-by-zero errors (handled by valid mask)
    old_settings = np.seterr(divide='ignore', invalid='ignore')
    t = (dp[..., 0] * d2[..., 1] - dp[..., 1] * d2[..., 0]) / cross
    u = (dp[..., 0] * d1[..., 1] - dp[..., 1] * d1[..., 0]) / cross
    np.seterr(**old_settings)
    
    valid = (np.abs(cross) >= 1e-10) & (t >= 0.0) & (t <= 1.0) & (u >= 0.0) & (u <= 1.0)
    
    return t, valid

def point_to_segment_distance(point: np.ndarray, seg_start: np.ndarray, seg_end: np.ndarray) -> float:
    seg_vec = seg_end - seg_start
    seg_len_sq = np.dot(seg_vec, seg_vec)
    if seg_len_sq == 0:
        return magnitude(point - seg_start)
  
    t = np.dot(point - seg_start, seg_vec) / seg_len_sq
    t = max(0.0, min(1.0, t))
    closest_point = seg_start + t * seg_vec
    return magnitude(point - closest_point)