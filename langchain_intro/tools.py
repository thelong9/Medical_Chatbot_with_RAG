import random
import time

def get_current_wait_time(hospital: str):
    """ Hàm dummy để tạo thời gian chờ ảo """
    if hospital not in ["A", "B", "C", "D"]:
        return f"Hospital {hospital} does not exist"
    
    # Cho chương trình dừng 1s
    time.sleep(1)
    
    return random.randint(0, 10000)
    
