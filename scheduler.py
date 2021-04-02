import icm
import time
import datetime

CHECK_PERIOD = 5  # minutes
START_HOUR = 22
END_HOUR = 0


def in_hour_range(start_hour, end_hour, current_hour):
    if start_hour < end_hour:
        return start_hour <= current_hour < end_hour
    else:
        return current_hour >= start_hour or current_hour < end_hour


def main():
    while True:
        hour = datetime.datetime.now().hour
        if in_hour_range(START_HOUR, END_HOUR, hour):
            icm.run()
        time.sleep(CHECK_PERIOD * 60)


if __name__ == '__main__':
    main()
