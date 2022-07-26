def minutes_sec_2_sec(t: str):
    min, sec = t.split(":")
    return int(min) * 60 + int(sec)
