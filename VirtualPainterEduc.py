# VirtualPainterEduc.py
import streamlit as st
import cv2
import numpy as np
import os
import time
import HandTrackingModule as htm
from KeyboardInput import KeyboardInput
import keyboard
from collections import deque
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av
import threading
from queue import Queue


class VirtualPainterProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = htm.handDetector(detectionCon=0.85)
        self.brushSize = 10
        self.eraserSize = 100
        self.drawColor = (255, 0, 255)  # Default pink
        self.xp, self.yp = 0, 0
        self.imgCanvas = np.zeros((720, 1280, 3), np.uint8)
        self.undoStack = []
        self.redoStack = []
        self.keyboard_input = KeyboardInput()
        self.last_time = time.time()
        self.show_guide = False
        self.current_guide_index = 0
        self.current_guide = None
        self.swipe_start_x = None
        self.swipe_active = False
        self.swipe_threshold = 50
        self.header = None
        self.guideList = []
        self.overlayList = []
        self.load_resources()

    def load_resources(self):
        # Load header images
        folderPath = 'header'
        myList = sorted(os.listdir(folderPath))
        self.overlayList = [cv2.imread(f"{folderPath}/{imPath}") for imPath in myList]
        self.header = self.overlayList[0]

        # Load guide images
        folderPath = 'guide'
        myList = sorted(os.listdir(folderPath))
        for imPath in myList:
            img = cv2.imread(f"{folderPath}/{imPath}")
            if img is not None:
                img = cv2.resize(img, (1280, 595))
                self.guideList.append(img)

    def save_state(self):
        return {
            'canvas': self.imgCanvas.copy(),
            'text_objects': list(self.keyboard_input.text_objects)
        }

    def restore_state(self, state):
        self.imgCanvas = state['canvas'].copy()
        self.keyboard_input.text_objects = deque(state['text_objects'], maxlen=20)

    def interpolate_points(self, x1, y1, x2, y2, num_points=10):
        points = []
        for i in range(num_points):
            x = int(x1 + (x2 - x1) * (i / num_points))
            y = int(y1 + (y2 - y1) * (i / num_points))
            points.append((x, y))
        return points

    def handle_keyboard_events(self):
        if self.keyboard_input.active:
            if keyboard.is_pressed('enter'):
                self.keyboard_input.process_key_input(13)
            elif keyboard.is_pressed('backspace'):
                self.keyboard_input.process_key_input(8)
            elif keyboard.is_pressed('esc'):
                self.keyboard_input.active = False
            elif keyboard.is_pressed('caps lock'):
                self.keyboard_input.caps_lock = not getattr(self.keyboard_input, 'caps_lock', False)
            else:
                shift_pressed = keyboard.is_pressed('shift')
                caps_lock_active = getattr(self.keyboard_input, 'caps_lock', False)

                # Handle numbers
                for num in '0123456789':
                    if keyboard.is_pressed(num):
                        if shift_pressed:
                            shift_num_map = {
                                '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
                                '6': '^', '7': '&', '8': '*', '9': '(', '0': ')'
                            }
                            char = shift_num_map[num]
                            self.keyboard_input.process_key_input(ord(char))
                        else:
                            self.keyboard_input.process_key_input(ord(num))
                        return

                # Handle letters
                for letter in 'abcdefghijklmnopqrstuvwxyz':
                    if keyboard.is_pressed(letter):
                        if shift_pressed ^ caps_lock_active:
                            self.keyboard_input.process_key_input(ord(letter.upper()))
                        else:
                            self.keyboard_input.process_key_input(ord(letter.lower()))
                        return

                # Handle special characters
                special_chars = {
                    'space': ' ', 'tab': '\t', '-': '-', '=': '=',
                    '[': '[', ']': ']', '\\': '\\', ';': ';', "'": "'",
                    ',': ',', '.': '.', '/': '/', '`': '`'
                }

                shifted_special_chars = {
                    '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
                    ';': ':', "'": '"', ',': '<', '.': '>', '/': '?', '`': '~'
                }

                for char in special_chars:
                    if keyboard.is_pressed(char):
                        if shift_pressed and char in shifted_special_chars:
                            self.keyboard_input.process_key_input(ord(shifted_special_chars[char]))
                        else:
                            self.keyboard_input.process_key_input(ord(special_chars[char]))
                        return

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        # Find Hand Landmarks
        img = self.detector.findHands(img, draw=False)
        lmList = self.detector.findPosition(img, draw=False)

        # Draw mode text
        cv2.putText(img, "Selection Mode - Two Fingers Up", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
        cv2.putText(img, "Selection Mode - Two Fingers Up", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            fingers = self.detector.fingersUp()

            # Selection Mode
            if fingers[1] and fingers[2]:
                self.xp, self.yp = 0, 0
                self.swipe_start_x = None

                if y1 < 125:
                    if 0 < x1 < 128:  # Save
                        self.header = self.overlayList[1]
                        self.save_canvas()
                        self.show_guide = False
                    elif 128 < x1 < 256:  # Pink
                        self.header = self.overlayList[2]
                        self.drawColor = (255, 0, 255)
                        self.show_guide = False
                        self.keyboard_input.active = False
                    elif 256 < x1 < 384:  # Blue
                        self.header = self.overlayList[3]
                        self.drawColor = (255, 0, 0)
                        self.show_guide = False
                        self.keyboard_input.active = False
                    elif 384 < x1 < 512:  # Green
                        self.header = self.overlayList[4]
                        self.drawColor = (0, 255, 0)
                        self.show_guide = False
                        self.keyboard_input.active = False
                    elif 512 < x1 < 640:  # Yellow
                        self.header = self.overlayList[5]
                        self.drawColor = (0, 255, 255)
                        self.show_guide = False
                        self.keyboard_input.active = False
                    elif 640 < x1 < 768:  # Eraser
                        self.header = self.overlayList[6]
                        self.drawColor = (0, 0, 0)
                        self.show_guide = False
                        self.keyboard_input.active = False
                        self.keyboard_input.delete_selected()
                    elif 768 < x1 < 896:  # Undo
                        self.header = self.overlayList[7]
                        if len(self.undoStack) > 0:
                            self.redoStack.append(self.save_state())
                            state = self.undoStack.pop()
                            self.restore_state(state)
                            self.show_guide = False
                    elif 896 < x1 < 1024:  # Redo
                        self.header = self.overlayList[8]
                        if len(self.redoStack) > 0:
                            self.undoStack.append(self.save_state())
                            state = self.redoStack.pop()
                            self.restore_state(state)
                            self.show_guide = False
                    elif 1024 < x1 < 1152:  # Guide
                        self.header = self.overlayList[9]
                        self.show_guide = True
                        self.current_guide_index = 0
                        self.current_guide = self.guideList[self.current_guide_index]
                        self.keyboard_input.active = False
                    elif 1155 < x1 < 1280:
                        if not self.keyboard_input.active:
                            self.keyboard_input.active = True
                        self.header = self.overlayList[10]
                        self.show_guide = False
                    elif 1155 < x1 < 1280 and y1 > 650:
                        if x1 < 1200:
                            if self.drawColor == (0, 0, 0):
                                self.eraserSize = max(10, self.eraserSize - 5)
                            else:
                                self.brushSize = max(1, self.brushSize - 1)
                        else:
                            if self.drawColor == (0, 0, 0):
                                self.eraserSize = min(200, self.eraserSize + 5)
                            else:
                                self.brushSize = min(50, self.brushSize + 1)
                        st.toast(
                            f"{'Eraser' if self.drawColor == (0, 0, 0) else 'Brush'} size: {self.eraserSize if self.drawColor == (0, 0, 0) else self.brushSize}")

                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), self.drawColor, cv2.FILLED)

            # Drawing Mode
            elif fingers[1] and not fingers[2] and not self.show_guide and not self.keyboard_input.active:
                self.swipe_start_x = None
                cv2.circle(img, (x1, y1), 15, self.drawColor, cv2.FILLED)

                if self.xp == 0 and self.yp == 0:
                    self.xp, self.yp = x1, y1

                points = self.interpolate_points(self.xp, self.yp, x1, y1)
                for point in points:
                    if self.drawColor == (0, 0, 0):  # eraser
                        cv2.line(img, (self.xp, self.yp), point, self.drawColor, self.eraserSize)
                        cv2.line(self.imgCanvas, (self.xp, self.yp), point, self.drawColor, self.eraserSize)
                    else:
                        cv2.line(img, (self.xp, self.yp), point, self.drawColor, self.brushSize)
                        cv2.line(self.imgCanvas, (self.xp, self.yp), point, self.drawColor, self.brushSize)
                    self.xp, self.yp = point

                self.undoStack.append(self.save_state())
                self.redoStack.clear()

            # Guide Navigation Mode
            elif fingers[1] and not fingers[2] and self.show_guide and not self.keyboard_input.active:
                if self.swipe_start_x is None:
                    self.swipe_start_x = x1
                    self.swipe_active = True
                else:
                    delta_x = x1 - self.swipe_start_x
                    if abs(delta_x) > self.swipe_threshold and self.swipe_active:
                        if delta_x > 0:
                            self.current_guide_index = max(0, self.current_guide_index - 1)
                        else:
                            self.current_guide_index = min(len(self.guideList) - 1, self.current_guide_index + 1)

                        self.current_guide = self.guideList[self.current_guide_index]
                        st.toast(f"Guide {self.current_guide_index + 1}/{len(self.guideList)}")
                        self.swipe_active = False

                    cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)

            # TEXT DRAGGING MODE - Two fingers, keyboard active
            elif self.keyboard_input.active and fingers[1] and fingers[2]:
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                if not self.keyboard_input.dragging:
                    if self.keyboard_input.text or self.keyboard_input.cursor_visible:
                        self.keyboard_input.check_drag_start(center_x, center_y)
                else:
                    self.keyboard_input.update_drag(center_x, center_y)
                    self.undoStack.append(self.save_state())
                    self.redoStack.clear()

                cv2.circle(img, (center_x, center_y), 15, (0, 255, 255), cv2.FILLED)

            else:
                self.xp, self.yp = 0, 0
                self.swipe_start_x = None
                self.swipe_active = False
                if self.keyboard_input.dragging:
                    self.keyboard_input.end_drag()

        else:
            self.swipe_start_x = None
            self.swipe_active = False
            if self.keyboard_input.dragging:
                self.keyboard_input.end_drag()

        self.handle_keyboard_events()
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.keyboard_input.update(dt)

        imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, self.imgCanvas)

        img[0:125, 0:1280] = self.header

        if self.keyboard_input.active:
            typing_area = np.zeros((100, 1280, 3), dtype=np.uint8)
            typing_area[:] = (50, 50, 50)
            img[620:720, 0:1280] = cv2.addWeighted(img[620:720, 0:1280], 0.7, typing_area, 0.3, 0)
            self.keyboard_input.draw(img)
            cv2.putText(img, "Press Enter to confirm text, ESC to cancel", (20, 700),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        else:
            self.keyboard_input.draw(img)

        if self.show_guide and self.current_guide is not None:
            guide_area = img[125:720, 0:1280].copy()
            blended_guide = cv2.addWeighted(self.current_guide, 0.3, guide_area, 0.3, 0)
            img[125:720, 0:1280] = blended_guide
            cv2.putText(img, f"Guide {self.current_guide_index + 1}/{len(self.guideList)}", (1100, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def run_virtual_painter():
    st.title("Beyond The Brush - Virtual Painter")

    # Add loading screen CSS
    st.markdown(
        """
        <style>
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
            height: 10px;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize the WebRTC streamer
    webrtc_ctx = webrtc_streamer(
        key="virtual-painter",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_processor_factory=VirtualPainterProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )


if __name__ == "__main__":
    run_virtual_painter()