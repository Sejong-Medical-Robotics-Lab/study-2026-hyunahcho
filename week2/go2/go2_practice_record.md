# Go2 Gazebo 수요일 실습 기록 — 2026-08-05

## 전체 목표

명령을 보낸다 → 로봇이 움직인다 → 상태 및 센서로 결과를 확인한다.

---

## 체크포인트 ① 환경 확인

- 완료 시각: 13:10경
- 성공 여부: 성공
- 작업공간: `~/go2_ws`
- 실행 명령:

bash source ~/go2_ws/install/setup.bash
ros2 launch go2_config gazebo.launch.py
확인 결과
Gazebo 정상 실행
Go2 모델 정상 표시
로봇이 바닥에 서 있는 상태 확인
마우스와 화면 정상 반응
반복되는 치명적 오류 없음
확인 당시 RTF: 약 0.39
진행안의 권장값인 0.8 이상보다는 낮았음
Gazebo와 RViz 등을 동시에 실행하면서 계산 부하가 증가한 것으로 보임

주요 토픽

데이터	실제 토픽	메시지 타입
---------------------------------------
속도 명령	/cmd_vel	geometry_msgs/msg/Twist
로봇 이동 상태	/odom	nav_msgs/msg/Odometry
LiDAR	/velodyne_points	sensor_msgs/msg/PointCloud2
관절 상태	/joint_states	sensor_msgs/msg/JointState
발 접촉 상태	/foot_contacts	champ_msgs/msg/ContactsStamped

체크포인트 ② Teleop과 상태 관찰

완료 시각: 13:15경
성공 여부: 성공
Teleop 조작
ros2 run teleop_twist_keyboard teleop_twist_keyboard

동작	키	/cmd_vel에서 변한 값
------------------------------------------
전진	i	linear.x 양수
후진	,	linear.x 음수
왼쪽 게걸음	J	linear.y
오른쪽 게걸음	L	linear.y
좌회전	j	angular.z 양수 또는 음수
우회전	l	angular.z 양수 또는 음수
정지	k	모든 속도 값 0
/odom 이동 전후 비교

이동 전
header.frame_id: odom
child_frame_id: base_footprint
position.x: 0.02657 m
position.y: 0.02595 m

이동 후
position.x: -0.25710 m
position.y: -0.22227 m
x방향 변화: 약 -0.284 m
y방향 변화: 약 -0.248 m
이동 거리: 약 0.38 m

로봇을 움직인 결과가 /odom 위치 값에 반영됨
/odom 발행 주기
average rate: 25.735 Hz
약 0.039초마다 메시지 발행
메시지 구조:
header
child_frame_id
pose
twist
covariance

체크포인트 ③ LiDAR와 RViz
완료 시각: 13:22경
성공 여부: 성공
실행
source ~/go2_ws/install/setup.bash
ros2 launch go2_config gazebo_velodyne.launch.py rviz:=true
LiDAR 토픽
/velodyne_points
sensor_msgs/msg/PointCloud2
LiDAR 메시지 확인 결과
frame_id: velodyne
height: 1
width: 3368
point_step: 22
row_step: 74096
data length: 74096
is_dense: true
LiDAR 발행 주기
average rate: 약 9.35 Hz
약 0.107초마다 한 번씩 점군 데이터 발행
RViz 확인
/velodyne_points PointCloud2 추가
Status: OK
Topic: /velodyne_points
로봇 주변 LiDAR 점군 정상 표시
Fixed Frame 정상 설정
테스트 박스 추가
기본 월드가 빈 공간이어서 1 m × 1 m × 1 m 박스를 추가함
박스 위치:
x = 2.0
y = 0.0
z = 0.5
관찰 결과
박스 앞면에 LiDAR 점이 촘촘하게 나타남
박스의 면과 모서리 형태를 확인함
박스 뒤쪽에는 LiDAR가 가려져 점이 비어 있는 영역이 나타남


체크포인트 ④ /cmd_vel 직접 발행
완료 시각: 13:35경
성공 여부: 성공
teleop 노드 종료 상태에서 진행하여 명령 충돌을 방지함
직진
linear.x = 0.2 또는 0.3
angular.z = 0.0
로봇이 전진 후 정상 정지함
제자리 회전
linear.x = 0.0
angular.z = 0.5
로봇이 제자리 회전 후 정상 정지함
원 궤적
linear.x = 0.3
angular.z = 0.3
직진과 회전 명령을 동시에 보내자 로봇이 곡선 경로로 이동함
사각형 경로 주행

파일:

~/robot_study/go2_week/square_path.py

설정값:

선속도: 0.3 m/s
각속도: 0.5 rad/s
직진 시간: 3.33초
회전 시간: 3.14초

동작 순서:

직진 → 정지 → 90도 좌회전 → 정지

위 과정을 4회 반복하여 사각형 경로 주행에 성공함.

체크포인트 ⑤ 조사 도구와 기록
완료 시각: 13:50경
성공 여부: 성공
rosbag 기록

녹화 토픽:

/velodyne_points
/odom

녹화 결과:

파일: sim_scan_0.db3
크기: 38.9 MiB
녹화 시간: 51.836초
전체 메시지: 2710개

토픽별 메시지 수:

/odom: 2237개
/velodyne_points: 473개
rqt_graph 관찰

확인한 명령 전달 경로:

/cmd_vel
→ /quadruped_controller_node
→ /joint_group_effort_controller/joint_trajectory

LiDAR 데이터 전달 경로:

/gazebo_ros_laser_controller
→ /velodyne_points

상태 추정 관련 경로:

/foot_contacts
→ /state_estimation_node
→ /odom
토픽 대역폭 비교
토픽	평균 대역폭	메시지 1개 크기
/cmd_vel	약 526 B/s	52 B
/odom	약 32 KB/s	0.72 KB
/velodyne_points	약 385 KB/s	약 81 KB
비교 결과
/cmd_vel은 속도 숫자만 포함하므로 데이터 크기가 가장 작음
/odom은 위치, 자세, 속도, covariance를 포함하므로 /cmd_vel보다 큼
/velodyne_points는 수천 개의 3차원 점 데이터를 포함하므로 가장 큰 대역폭을 사용함



막힌 점과 해결 방법
1. Gazebo 실행 중 컴퓨터 멈춤
현상:
화면과 마우스, 키보드 입력이 모두 멈춤
조치:
전원 버튼을 길게 눌러 강제 종료 후 재부팅
재부팅 후 메모리 상태 확인
총 RAM: 30 GiB
사용 가능: 27 GiB
Swap 사용: 0 B
판단:
RAM 부족 문제는 아니었음
일시적인 Gazebo 또는 그래픽 처리 문제일 가능성이 있음
해결:
불필요한 프로그램과 지속 출력 터미널을 줄임
timeout과 --once를 사용하여 장시간 출력되는 명령을 제한함
이후 Gazebo와 RViz가 정상적으로 동작함
2. 기본 월드에 장애물이 없음
문제:
LiDAR로 장애물 윤곽과 가림 현상을 관찰하기 어려웠음
해결:
/tmp/box.sdf 파일을 생성하고 Gazebo에 테스트 박스를 추가함
RViz에서 박스 표면과 뒤쪽 가림 영역을 확인함


실습을 통해 이해한 내용
/cmd_vel은 로봇에 원하는 선속도와 각속도를 전달하는 명령 토픽이다.
/odom은 로봇의 위치, 자세, 선속도, 각속도를 포함하는 상태 토픽이다.
LiDAR 데이터는 PointCloud2 메시지로 전달되며 RViz에서 점군으로 표시할 수 있다.
linear.x와 angular.z를 동시에 사용하면 로봇을 곡선 경로로 움직일 수 있다.
ROS2 노드와 토픽의 연결 관계는 rqt_graph로 확인할 수 있다.
rosbag을 이용하면 실시간 센서와 상태 데이터를 저장한 뒤 다시 분석할 수 있다.
토픽마다 메시지 구조와 발행 주기가 다르며, LiDAR처럼 데이터가 많은 센서는 높은 대역폭을 사용한다.


한 줄 소감

Go2에 직접 속도 명령을 보내고, 로봇의 움직임을 /odom과 LiDAR 데이터로 다시 확인하면서 ROS2의 명령·상태·센서 흐름을 실제로 이해할 수 있었다. 실제 Gazebo 시뮬레이션과 go2의 이동을 보니 신기했으며, Rviz와 Gazebo의 차이도 더 잘 이해할 수 있었다.
