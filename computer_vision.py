from time import sleep, time

import cv2  # computer vision
import mediapipe as mp  # pre-trained models lib -> hand-detection
import serial  # Import pyserial
import keyboard

# hand detection logic
class HandSignalDetector:
    # constructor
    def __init__(self):
        # Hands Module
        self.mp_hands = mp.solutions.hands
        # init: live video, only detect one hand, confidence det level threshold
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        # drawing utilities
        self.mp_draw = mp.solutions.drawing_utils
        # Serial communication setup
        self.arduino = serial.Serial('COM6', 9600, timeout=1)  # Replace 'COM3' with your Arduino's COM port
        self.last_sent_to_arduino = time()

    def detect_hands(self, frame):
        # convert captured frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # detected hand landmarks (if any)
        result = self.hands.process(rgb_frame)
        return result

    def recognize_fingers(self, hand_landmarks):
        # fingertip landmarks (indices for index, pinky, etc.)
        finger_tips = [8, 12, 16, 20]
        lifted_fingers = []

        for tip_id in finger_tips:
            # Get tip and DIP joint landmark positions
            # tip: fingertip landmark position
            # dip: position of the joint two steps below the tip
            tip = hand_landmarks.landmark[tip_id]
            dip = hand_landmarks.landmark[tip_id - 2]

            # check if fingertip is above its DIP joint (indicating a lifted finger)
            if tip.y < dip.y:  # Y-coordinate decreases upward
                lifted_fingers.append(tip_id)

        return lifted_fingers

    def draw_landmarks(self, frame, hand_landmarks):
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def send_signal_to_arduino(self, lifted_fingers):
        self.last_sent_to_arduino = time()
        # Check specific conditions based on raised fingers
        if lifted_fingers == [20]:  # Only pinky is raised
            self.arduino.write(b'CMD:MOVE_LEFT\n')  # Send '-1'
            print('CMD:MOVE_LEFT')
        elif lifted_fingers == [8]:  # Only index is raised
            self.arduino.write(b'CMD:MOVE_RIGHT\n')  # Send '1'
            print('CMD:MOVE_RIGHT')
        elif lifted_fingers == [8, 20]:  # Only index and pinky are raised
            self.arduino.write(b'CMD:SHOOT\n')  # Send '0'
            print('CMD:SHOOT')
        elif lifted_fingers == [8, 12, 16, 20]:
            self.arduino.write(b'CHANGE\n')
            print('CHANGE')
        else:
            self.arduino.write(b'0\n')  # Default to '0' if none of the conditions match

def main():
    detector = HandSignalDetector()
    cap = cv2.VideoCapture(0)   # webcam connection

    while cap.isOpened():
        ret, frame = cap.read()     # ret = whether the frame was successfully read
        if not ret:
            break

        # Detect hands
        result = detector.detect_hands(frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # recognize fingers
                lifted_fingers = detector.recognize_fingers(hand_landmarks)
                # draw landmarks
                detector.draw_landmarks(frame, hand_landmarks)

                detector.send_signal_to_arduino(lifted_fingers)  # Send signal to Arduino
        # show the annotated frame in a window
        cv2.imshow("Hand Signal Detector", frame)

        # exit condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()   # close webcam connection
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
