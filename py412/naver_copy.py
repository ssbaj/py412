"""
F9 트리거 - 마우스 드래그 + 스크롤 자동 복사 프로그램 (1회 실행 후 종료)
--------------------------------------------------------------------
사용법:
1. pip install pynput pyautogui pyperclip
2. 이 스크립트를 실행한다.
3. 복사하고 싶은 텍스트 영역의 시작 지점에서 마우스 왼쪽 버튼을 누른 채로 유지한다
   (일반적인 드래그 선택처럼, 버튼은 계속 누르고 있어야 함).
4. 왼쪽 버튼을 누른 상태에서 F9 키를 누르면:
   - 커서가 오른쪽으로 약 4cm 이동한다.
   - 이후 "Ctrl+C 복사 -> 클립보드 읽기 -> 아래로 스크롤"을 반복한다.
5. 스크롤이 끝나는 지점(원하는 곳)에서 마우스 왼쪽 버튼을 떼면
   자동 반복이 즉시 멈추고, 그동안 복사된 전체 텍스트를
   저장 시각(분 단위)이 포함된 파일명(예: my_copy202607301716.txt)으로 저장한 뒤
   프로그램이 자동으로 종료된다.

주의:
- 실제로 마우스 왼쪽 버튼을 물리적으로 누르고 있는 상태를 그대로 유지해야
  텍스트 선택(드래그)이 이어진다. 이 스크립트는 버튼을 대신 누르거나 떼지 않고,
  커서 이동/스크롤/Ctrl+C 만 자동으로 수행한다.
- Windows 디스플레이 배율(예: 125%, 150%)에 따라 "4cm"의 실제 픽셀 값이 달라질 수
  있으니 필요하면 PIXELS_PER_CM 값을 조정한다.
"""

import threading
import time
from datetime import datetime

import pyautogui
import pyperclip
from pynput import keyboard, mouse

# ------------------------- 설정값 (필요에 맞게 조정) -------------------------
PIXELS_PER_CM = 37.8     # 96dpi 기준 대략값 (2.54cm = 1inch = 96px)
MOVE_RIGHT_CM = 4        # F9를 누르면 오른쪽으로 이동할 거리(cm)
SCROLL_AMOUNT = -300     # 1회당 스크롤 양 (음수 = 아래로, pyautogui 기준)
LOOP_INTERVAL = 0.4      # 복사 -> 스크롤 반복 간격(초)
COPY_SETTLE_DELAY = 0.1  # Ctrl+C 이후 클립보드에 반영될 때까지 대기 시간(초)
OUTPUT_FILE_PREFIX = "my_copy"  # 저장 시 뒤에 YYYYMMDDHHMM.txt 형태의 타임스탬프가 붙는다
# -----------------------------------------------------------------------------

kbd_controller = keyboard.Controller()

state_lock = threading.Lock()
left_button_down = False
loop_active = False

# 선택 영역이 "이어서 커지는" 일반적인 경우와, 가상 스크롤(채팅창 등)처럼
# 위쪽 내용이 선택에서 빠져버리는 경우를 모두 다루기 위한 누적 로직.
finalized_parts = []
current_chunk = ""

# 저장 완료 후 리스너를 멈춰 프로그램을 종료시키기 위한 참조
mouse_listener = None
keyboard_listener = None


def do_copy():
    """Ctrl+C 를 눌러 현재 선택 영역을 클립보드로 복사한다."""
    kbd_controller.press(keyboard.Key.ctrl)
    kbd_controller.press("c")
    kbd_controller.release("c")
    kbd_controller.release(keyboard.Key.ctrl)


def absorb_clipboard():
    """클립보드를 읽어 누적 버퍼(finalized_parts/current_chunk)에 반영한다."""
    global current_chunk

    text = pyperclip.paste()
    if not text or text == current_chunk:
        return

    if text.startswith(current_chunk):
        # 선택 영역이 이어서 커진 정상적인 경우 -> 그냥 교체
        current_chunk = text
    else:
        # 이전 내용이 선택에서 빠진 경우(가상 스크롤 등) -> 이전 조각을 확정하고 새로 시작
        if current_chunk:
            finalized_parts.append(current_chunk)
        current_chunk = text


def scroll_and_copy_loop():
    global loop_active, current_chunk

    move_px = int(MOVE_RIGHT_CM * PIXELS_PER_CM)
    pyautogui.moveRel(move_px, 0, duration=0.2)

    while True:
        with state_lock:
            if not left_button_down:
                break

        do_copy()
        time.sleep(COPY_SETTLE_DELAY)
        absorb_clipboard()

        pyautogui.scroll(SCROLL_AMOUNT)
        time.sleep(LOOP_INTERVAL)

    # 버튼을 뗀 순간 마지막으로 한 번 더 복사해서 반영
    do_copy()
    time.sleep(COPY_SETTLE_DELAY)
    absorb_clipboard()

    save_result()

    with state_lock:
        loop_active = False

    # 저장이 끝났으므로 리스너를 멈춰 프로그램을 종료한다.
    if mouse_listener is not None:
        mouse_listener.stop()
    if keyboard_listener is not None:
        keyboard_listener.stop()


def save_result():
    global finalized_parts, current_chunk

    if current_chunk:
        finalized_parts.append(current_chunk)
        current_chunk = ""

    final_text = "\n".join(finalized_parts)

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    output_file = f"{OUTPUT_FILE_PREFIX}{timestamp}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"[완료] {output_file} 에 저장했습니다. (총 {len(finalized_parts)}개 조각)")
    print("프로그램을 종료합니다.")
    finalized_parts = []


def on_click(x, y, button, pressed):
    global left_button_down
    if button == mouse.Button.left:
        with state_lock:
            left_button_down = pressed


def on_press(key):
    global loop_active
    if key == keyboard.Key.f9:
        with state_lock:
            if left_button_down and not loop_active:
                loop_active = True
                threading.Thread(target=scroll_and_copy_loop, daemon=True).start()


def main():
    global mouse_listener, keyboard_listener

    print("프로그램 시작.")
    print("마우스 왼쪽 버튼을 누른 채 F9를 누르면 자동 스크롤+복사가 시작됩니다.")
    print("왼쪽 버튼을 떼면 my_copy<날짜시각>.txt 로 저장하고 프로그램이 종료됩니다.")

    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener.start()
    keyboard_listener.start()
    mouse_listener.join()
    keyboard_listener.join()


if __name__ == "__main__":
    main()

