# import time
# import os
# import sys
# import cv2
# import mediapipe as mp  # type:ignore

# capture = cv2.VideoCapture(0)

# mpHands = mp.solutions.hands
# hands = mpHands.Hands()
# mpDraw = mp.solutions.drawing_utils

# while True:
#     success, img = capture.read()
#     rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     result = hands.process(rgb_image)
#     # cv2.waitKey(1)
#     # print(result.multi_hand_landmarks)
#     if result.multi_hand_landmarks:
#         for mlm in result.multi_hand_landmarks:
#             mpDraw.draw_landmarks(img, mlm, mpHands.HAND_CONNECTIONS,
#                                   mpDraw.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=2), mpDraw.DrawingSpec(color=(0, 255, 0), thickness=3))
#             print("Wah kya scene hai")
#             middle_finger_tip = mlm.landmark[12]
#             middle_finger_root = mlm.landmark[9]
#             if middle_finger_tip.y < middle_finger_root.y:
#                 break
#             else:
#                 print("Haat uppar karna lodu")

#     cv2.imshow("Image", img)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         print("Haan chal maa chuda")
#         break
# capture.release()
# cv2.destroyAllWindows()

# # capture.release()
# # cv2.destroyAllWindows()
import cv2
import mediapipe as mp

capture = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mpDraw = mp.solutions.drawing_utils

try:
    while capture.isOpened():

        success, img = capture.read()

        if not success:
            print("Camera not responding")
            break

        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_image)

        if result.multi_hand_landmarks:

            for mlm in result.multi_hand_landmarks:

                mpDraw.draw_landmarks(
                    img,
                    mlm,
                    mpHands.HAND_CONNECTIONS,
                    mpDraw.DrawingSpec(
                        color=(0, 255, 0),
                        thickness=3,
                        circle_radius=2
                    ),
                    mpDraw.DrawingSpec(
                        color=(0, 255, 0),
                        thickness=3
                    )
                )

                # Finger landmarks
                index_tip = mlm.landmark[8]
                middle_tip = mlm.landmark[12]
                ring_tip = mlm.landmark[16]
                pinky_tip = mlm.landmark[20]

                index_pip = mlm.landmark[6]
                middle_pip = mlm.landmark[10]
                ring_pip = mlm.landmark[14]
                pinky_pip = mlm.landmark[18]

                # Check finger positions
                index_folded = index_tip.y > index_pip.y
                middle_raised = middle_tip.y < middle_pip.y
                ring_folded = ring_tip.y > ring_pip.y
                pinky_folded = pinky_tip.y > pinky_pip.y

                # Detect gesture
                if (
                    middle_raised
                    and index_folded
                    and ring_folded
                    and pinky_folded
                ):
                    cv2.putText(
                        img,
                        "GESTURE DETECTED - EXITING",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

                    cv2.imshow("Image", img)
                    cv2.waitKey(500)

                    print("Middle finger detected. Shutting down.")
                    break

        # Display camera
        cv2.imshow("Image", img)

        # EMERGENCY SHUTDOWN
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            print("Manual shutdown.")
            break

        # Detect if window was closed manually
        if cv2.getWindowProperty(
            "Image", cv2.WND_PROP_VISIBLE
        ) < 1:
            print("Window closed manually.")
            break

        # Check if gesture was detected
        if result.multi_hand_landmarks:
            if (
                middle_raised
                and index_folded
                and ring_folded
                and pinky_folded
            ):
                break

finally:
    capture.release()
    hands.close()
    cv2.destroyAllWindows()
    print("Program terminated.")
