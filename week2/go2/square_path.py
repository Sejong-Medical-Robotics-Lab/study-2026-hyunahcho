#!/usr/bin/env python3

import subprocess
import time


LINEAR_SPEED = 0.3
ANGULAR_SPEED = 0.5

FORWARD_TIME = 3.33
TURN_TIME = 3.14

CMD_VEL_TOPIC = "/cmd_vel"
TWIST_TYPE = "geometry_msgs/msg/Twist"


def publish_for_duration(message: str, duration: float) -> None:
    """지정한 Twist 메시지를 10 Hz로 일정 시간 동안 발행한다."""
    command = [
        "ros2",
        "topic",
        "pub",
        "--rate",
        "10",
        CMD_VEL_TOPIC,
        TWIST_TYPE,
        message,
    ]

    process = subprocess.Popen(command)

    try:
        time.sleep(duration)
    finally:
        process.terminate()

        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def stop_robot() -> None:
    stop_message = (
        "{linear: {x: 0.0, y: 0.0, z: 0.0}, "
        "angular: {x: 0.0, y: 0.0, z: 0.0}}"
    )

    subprocess.run(
        [
            "ros2",
            "topic",
            "pub",
            "--once",
            CMD_VEL_TOPIC,
            TWIST_TYPE,
            stop_message,
        ],
        check=True,
    )


def move_forward() -> None:
    forward_message = (
        f"{{linear: {{x: {LINEAR_SPEED}, y: 0.0, z: 0.0}}, "
        "angular: {x: 0.0, y: 0.0, z: 0.0}}"
    )

    publish_for_duration(forward_message, FORWARD_TIME)
    stop_robot()
    time.sleep(1.0)


def turn_left() -> None:
    turn_message = (
        "{linear: {x: 0.0, y: 0.0, z: 0.0}, "
        f"angular: {{x: 0.0, y: 0.0, z: {ANGULAR_SPEED}}}}}"
    )

    publish_for_duration(turn_message, TURN_TIME)
    stop_robot()
    time.sleep(1.0)


def main() -> None:
    try:
        for side in range(1, 5):
            print(f"{side}번째 변 직진")
            move_forward()

            print(f"{side}번째 90도 좌회전")
            turn_left()

        print("사각형 경로 주행 완료")

    except KeyboardInterrupt:
        print("\n사용자 중단")

    finally:
        stop_robot()


if __name__ == "__main__":
    main()
