# Hand Gesture Recognition: A Beginner's Guide

This README teaches you **every part** of `hand_tracking.py`. No prior knowledge beyond basic Python is assumed. Read it top to bottom, and type the code yourself as you go.

---

## 1. What does this program do?

1. Opens your webcam.
2. Reads one picture (a *frame*) from it, over and over, very fast. That is what makes it a video.
3. Asks **MediaPipe** (a hand-detection library made by Google) to find your hand in each frame.
4. Draws a green skeleton on your hand.
5. Checks which fingers are up or down.
6. If **only the middle finger is up**, it shows a warning and shuts down.
7. You can also quit with `q` or `Esc`, or by closing the window.

---

## 2. Setup

Install the two libraries:

```bash
pip install opencv-python mediapipe
```

Save the program as `hand_tracking.py`, then run:

```bash
python hand_tracking.py
```

> **Note:** This code uses `mp.solutions.hands`, which is the classic MediaPipe API. If you get an error like `module 'mediapipe' has no attribute 'solutions'`, install a version that still includes it: `pip install mediapipe==0.10.14`.

---

## 3. The big picture (read this first)

```
Open camera
    |
    v
+-----------------------------+
|  LOOP (repeats forever)     |
|                             |
|  1. Grab a frame            |
|  2. Convert colours         |
|  3. Ask MediaPipe: hand?    |
|  4. If yes: draw it         |
|  5. Check fingers           |
|  6. Middle finger? -> stop  |
|  7. Show the frame          |
|  8. 'q' pressed? -> stop    |
+-----------------------------+
    |
    v
Clean up (release camera, close windows)
```

Everything in the code fits into this picture. When you get lost, come back here.

---

## 4. Concepts you need first

| Word | Plain-English meaning | Example in this program |
|---|---|---|
| **Library** | Pre-written code you borrow | `cv2`, `mediapipe` |
| **Variable** | A labelled box that stores something | `capture`, `img` |
| **Function** | A named set of instructions you can run | `cv2.imshow(...)` |
| **Object** | A thing that holds data *and* abilities | `capture` |
| **Method** | A function that belongs to an object | `capture.isOpened()` |
| **Boolean** | A value that is only `True` or `False` | `middle_raised` |
| **Loop** | Repeat code again and again | `while`, `for` |
| **Condition** | "Do this only if..." | `if not success:` |
| **Tuple** | A fixed group of values in `( )` | `(0, 255, 0)` |

If any row feels fuzzy, don't worry. You'll see each one in action below.

---

## 5. The code, piece by piece

### 5.1 Imports

```python
import cv2
import mediapipe as mp
```

- `import cv2` brings in **OpenCV**, which handles cameras, images, and windows.
- `import mediapipe as mp` brings in **MediaPipe**. `as mp` gives it a short nickname so you can write `mp.` instead of `mediapipe.` every time.

### 5.2 Opening the camera

```python
capture = cv2.VideoCapture(0)
```

- `cv2.VideoCapture(0)` connects to a camera. `0` means "default webcam", `1` would be a second camera.
- The connection is stored in the variable `capture`. We store it because we need to use it **many times later** (to read frames, to check it's open, to release it). If we didn't save it, we'd lose the connection immediately.

### 5.3 Setting up MediaPipe

```python
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mpDraw = mp.solutions.drawing_utils
```

- `mpHands` is the hand-tracking module.
- `hands = mpHands.Hands(...)` creates the actual **hand detector** and stores it in `hands`. The things inside the brackets are *settings*:
  - `max_num_hands=1` means look for at most one hand. This makes it faster and simpler.
  - `min_detection_confidence=0.7` means only accept a hand if MediaPipe is at least 70% sure it's a hand.
  - `min_tracking_confidence=0.7` means once a hand is found, keep following it only while at least 70% sure.
- `mpDraw` is a helper that draws the skeleton on the image.

### 5.4 The `try` / `finally` safety net

```python
try:
    while capture.isOpened():
        ...
finally:
    capture.release()
    hands.close()
    cv2.destroyAllWindows()
    print("Program terminated.")
```

- Code inside `try:` is the main work.
- Code inside `finally:` **always runs at the end**, even if the program crashes or you break out of the loop.
- Why does that matter? A camera is a shared resource. If your program never lets go of it, other apps can't use it. So `finally` guarantees we release the camera, close the detector, and close the windows.

### 5.5 The main loop

```python
while capture.isOpened():
```

`while` means "keep repeating the indented code as long as this is `True`". Here: keep going while the camera is open. Each repeat of the loop handles **one frame**.

### 5.6 Reading a frame

```python
success, img = capture.read()

if not success:
    print("Camera not responding")
    break
```

- `capture.read()` returns **two things at once**:
  1. `success`: `True` if a frame was captured, `False` if not.
  2. `img`: the frame itself (a picture stored as numbers).
- Writing `success, img = ...` is called **unpacking**. It puts the first value in `success` and the second in `img`.
- `if not success:` means "if reading failed". Then we print a message and `break`, which immediately exits the loop.

### 5.7 Converting colours

```python
rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
result = hands.process(rgb_image)
```

- OpenCV stores colours in the order **B**lue, **G**reen, **R**ed. MediaPipe expects **R**ed, **G**reen, **B**lue. If we skip the conversion, detection works worse because the colours are mixed up.
- `cv2.cvtColor(...)` converts the image, and we save the converted copy in `rgb_image`.
- `hands.process(rgb_image)` runs the detector. Everything it finds is stored in `result`.

### 5.7b What's inside `result`?

`result.multi_hand_landmarks` is:
- a **list of hands** if any were found (we only allow 1),
- `None` if no hand was found.

That's why the next line is an `if`.

### 5.8 Drawing the hand

```python
if result.multi_hand_landmarks:

    for mlm in result.multi_hand_landmarks:

        mpDraw.draw_landmarks(
            img,
            mlm,
            mpHands.HAND_CONNECTIONS,
            mpDraw.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=2),
            mpDraw.DrawingSpec(color=(0, 255, 0), thickness=3)
        )
```

- `if result.multi_hand_landmarks:` means "if at least one hand was found". An empty or `None` value counts as `False`.
- `for mlm in ...` is a **for loop**. It goes through each detected hand, one at a time, calling the current one `mlm` ("multi landmarks"). Since we allowed only 1 hand, it runs once.
- `draw_landmarks(...)` draws on `img`:
  - the points (joints) of the hand,
  - the lines connecting them (`HAND_CONNECTIONS`),
  - styled with `DrawingSpec`. Colour `(0, 255, 0)` is **green** in (Blue, Green, Red) order.

### 5.9 Landmarks: the heart of the whole program

MediaPipe finds **21 points** on your hand, numbered 0 to 20:

```
        8   12  16  20          <- fingertips
        |    |   |   |
        7   11  15  19
   4    |    |   |   |
   |    6   10  14  18          <- PIP joint (middle knuckle)
   3    |    |   |   |
   |    5    9  13  17          <- base of each finger
   2     \   |  /   /
   |      \  | /  /
   1       \ |/  /
    \       \|  /
     \_______0                  <- wrist
```

| Finger | Base | Middle joint (PIP) | Tip |
|---|---|---|---|
| Thumb | 1 | 2 / 3 | **4** |
| Index | 5 | **6** | **8** |
| Middle | 9 | **10** | **12** |
| Ring | 13 | **14** | **16** |
| Pinky | 17 | **18** | **20** |

(Bold numbers are the ones this program uses.)

Each point has three values:
- `.x`: horizontal position, from `0.0` (left edge) to `1.0` (right edge)
- `.y`: vertical position, from `0.0` (top edge) to `1.0` (bottom edge)
- `.z`: depth (not used here)

### 5.10 Reading the landmarks

```python
index_tip = mlm.landmark[8]
middle_tip = mlm.landmark[12]
ring_tip = mlm.landmark[16]
pinky_tip = mlm.landmark[20]

index_pip = mlm.landmark[6]
middle_pip = mlm.landmark[10]
ring_pip = mlm.landmark[14]
pinky_pip = mlm.landmark[18]
```

`mlm.landmark` is a list of all 21 points. `[8]` picks point number 8. We save the tip and the middle joint of each finger in clearly named variables so the code reads like English.

> Note: Python counts from **0**, so `landmark[0]` is the first point (the wrist).

### 5.11 The key idea: is a finger up or down?

**In images, `y` grows going DOWN.** The top of the screen is `y = 0` and the bottom is `y = 1`. This surprises almost every beginner.

So:
- A **smaller** `y` means **higher** on the screen.
- If a fingertip is **higher** than its middle joint, the finger is **straight up**.

```python
index_folded  = index_tip.y > index_pip.y    # tip is lower than joint -> curled
middle_raised = middle_tip.y < middle_pip.y  # tip is higher than joint -> up
ring_folded   = ring_tip.y > ring_pip.y
pinky_folded  = pinky_tip.y > pinky_pip.y
```

Each line **compares two numbers** and stores the answer (`True` or `False`) in a variable. These `True`/`False` variables are **booleans**.

Visual check:

```
Finger UP:                Finger FOLDED:

   tip  (y = 0.30)           pip  (y = 0.50)
    |                        / 
   pip  (y = 0.50)         tip  (y = 0.60)

tip.y < pip.y  -> UP      tip.y > pip.y  -> FOLDED
```

### 5.12 Detecting the gesture

```python
if (
    middle_raised
    and index_folded
    and ring_folded
    and pinky_folded
):
```

`and` means **all of these must be `True`** at the same time. So the whole condition is true only when:
- the middle finger is up, **and**
- the index finger is folded, **and**
- the ring finger is folded, **and**
- the pinky is folded.

If even one is `False`, the whole thing is `False`. (The other logical operators are `or`, meaning at least one is true, and `not`, which flips a value.)

### 5.13 Reacting to the gesture

```python
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
```

`cv2.putText` writes text onto the image. Its arguments, in order:

| Argument | Meaning |
|---|---|
| `img` | which picture to write on |
| `"GESTURE DETECTED..."` | the text |
| `(20, 50)` | position: 20 px from the left, 50 px from the top |
| `cv2.FONT_HERSHEY_SIMPLEX` | the font |
| `0.8` | text size |
| `(0, 0, 255)` | colour: **red** (Blue=0, Green=0, Red=255) |
| `2` | line thickness |

Then:
- `cv2.imshow("Image", img)` shows the frame so you see the message.
- `cv2.waitKey(500)` pauses for 500 milliseconds so you actually have time to read it.
- `break` exits the **`for` loop** (the closest loop around it).

### 5.14 Showing the video

```python
cv2.imshow("Image", img)
```

This displays the current frame in a window titled `"Image"`. Because it runs inside the `while` loop, you see a new frame many times per second. That's your live video.

### 5.15 Keyboard shutdown

```python
key = cv2.waitKey(1) & 0xFF

if key == ord('q') or key == 27:
    print("Manual shutdown.")
    break
```

- `cv2.waitKey(1)` waits 1 millisecond for a key press. **It is also required to make the window refresh**, so never delete it.
- `& 0xFF` is a small technical trick that keeps just the last 8 bits of the number, so the key code is reliable across systems. You can treat it as a standard recipe for now.
- `ord('q')` gives the number code for the letter `q`. `27` is the code for the **Esc** key.
- `or` means either key works.
- `break` exits the `while` loop, because this `if` sits directly inside it.

### 5.16 Detecting a closed window

```python
if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
    print("Window closed manually.")
    break
```

If you click the window's X button, its "visible" property drops below 1. We notice that and exit cleanly instead of crashing.

### 5.17 Exiting the main loop after the gesture

```python
if result.multi_hand_landmarks:
    if (
        middle_raised
        and index_folded
        and ring_folded
        and pinky_folded
    ):
        break
```

Remember: the earlier `break` (section 5.13) only escaped the `for` loop. This **second check** is what escapes the `while` loop, so the program actually ends.

Why check `if result.multi_hand_landmarks` first? If no hand is visible, the variables like `middle_raised` were **never created** in that frame, and using them would crash with a `NameError`. The `if` guard protects us.

### 5.18 Cleanup

```python
finally:
    capture.release()
    hands.close()
    cv2.destroyAllWindows()
    print("Program terminated.")
```

- `capture.release()` gives the camera back to your computer.
- `hands.close()` shuts down the MediaPipe detector.
- `cv2.destroyAllWindows()` closes every OpenCV window.

---

## 6. Trace one frame (try this on paper)

Imagine your hand shows only the middle finger:

1. `capture.read()` returns `success = True` and a picture.
2. The picture is converted to RGB.
3. MediaPipe finds the hand, so `result.multi_hand_landmarks` has one entry.
4. The skeleton is drawn.
5. Landmark 12 (middle tip) is higher than landmark 10, so `middle_raised = True`.
6. The other three fingers are curled, so all three `*_folded` are `True`.
7. The big `and` condition is `True`, so we print the red message, wait half a second, and `break` the `for` loop.
8. The frame is shown, then the second check `break`s the `while` loop.
9. `finally` runs, the camera is released, and the program ends.

---

## 7. Known limitations (good to understand, not bugs to panic about)

1. **The thumb is ignored.** The thumb moves sideways, not up and down, so the `y` comparison doesn't work for it. You'd compare `x` values instead.
2. **Your hand must be upright.** Everything relies on "up means smaller `y`". If you rotate your hand sideways, the logic breaks.
3. **The image isn't mirrored.** Moving your hand right looks like it moves left on screen. `img = cv2.flip(img, 1)` right after `capture.read()` fixes that.
4. **The gesture code appears twice.** The same condition is written in two places. In Stage 6 of your course, you'll turn it into a function so you write it once.

---

## 8. Common errors

| Error | Likely cause | Fix |
|---|---|---|
| `Camera not responding` | Another app is using the camera, or wrong index | Close other apps, try `VideoCapture(1)` |
| `ModuleNotFoundError: cv2` | OpenCV isn't installed | `pip install opencv-python` |
| `no attribute 'solutions'` | Newer MediaPipe version | `pip install mediapipe==0.10.14` |
| `NameError: middle_raised` | Using the variable when no hand was detected | Keep it inside the `if result.multi_hand_landmarks:` block |
| Window freezes or stays blank | Missing `cv2.waitKey(1)` | Keep it in the loop |

---

## 9. Exercises (do these to really learn)

Try each one **without** looking for the answer first. Change one thing at a time and run it.

**Easy**
1. Change the skeleton colour from green to blue.
2. Change the quit key from `q` to `x`.
3. Add `img = cv2.flip(img, 1)` and observe what changes.

**Medium**
4. Print `index_tip.y` every frame. Move your finger up and down and watch the number change. This is the best way to *see* the coordinate system.
5. Add a new boolean `index_raised = index_tip.y < index_pip.y`.
6. Write on screen "PEACE" when **index and middle are up, and ring and pinky are folded**.

**Challenging**
7. Create an **open palm** gesture (all four fingers raised).
8. Create a **fist** gesture (all four fingers folded).
9. Write a function `is_finger_raised(tip, pip)` that returns `True` or `False`, and use it to shorten the code.
10. Detect the thumb using `x` coordinates.

---

## 10. Glossary

- **Frame**: one single picture from the video.
- **Landmark**: one of the 21 tracked points on the hand.
- **Boolean**: a value that is `True` or `False`.
- **Unpacking**: assigning several values at once (`a, b = ...`).
- **Break**: immediately exit the nearest loop.
- **Index (list)**: the position number of an item, starting at 0.
- **Tuple**: a fixed group of values like `(0, 255, 0)`.
- **BGR/RGB**: the order in which colour channels are stored.

---

*Next step: do exercises 4 to 6 first. When you've finished them, you'll be ready to design your own gestures.*
