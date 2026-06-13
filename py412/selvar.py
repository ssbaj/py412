import tkinter as tk
import pandas as pd
import inspect
import threading
import pyautogui
import time

class VariableSelector:
    def __init__(self, df_obj, df_name):
        if not isinstance(df_obj, pd.DataFrame):
            print("The input must be a pandas DataFrame.")
            return
            
        self.df_obj = df_obj
        self.df_name = df_name
        self.ordered_indices = []
        
        # GUI를 별도 쓰레드에서 실행
        self.thread = threading.Thread(target=self._run_gui, daemon=True)
        self.thread.start()

    def _run_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Vars: {self.df_name}")
        self.root.geometry("350x650") # 버튼 추가를 고려해 높이 조절
        self.root.attributes("-topmost", True)
        
        default_font = ("Malgun Gothic", 10)
        
        tk.Label(self.root, text=f"DATA FRAME : {self.df_name}", 
                 fg="#2c3e50", font=(default_font[0], 10, "bold")).pack(pady=10)
        
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.listbox = tk.Listbox(list_frame, selectmode="multiple", background="white", 
                                  font=default_font, highlightthickness=1, exportselection=False)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        # 초기 변수 목록 로드
        self.refresh_list()
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # --- 기능 버튼들 ---
        tk.Button(btn_frame, text="📄 Insert Simple List", command=self.insert_simple, font=default_font).pack(fill="x", pady=2)
        tk.Button(btn_frame, text="📈 Insert Formula", command=self.insert_lm, font=default_font, bg="#e1f5fe").pack(fill="x", pady=2)
        
        # [추가됨] 변수 업데이트 버튼: 데이터프레임의 최신 컬럼을 다시 읽어옴
        tk.Button(btn_frame, text="🔄 Update Variables", command=self.refresh_list, font=default_font, bg="#f0f4c3").pack(fill="x", pady=2)
        
        tk.Button(btn_frame, text="❌ Close", command=self.root.destroy, font=default_font).pack(fill="x", pady=5)
        
        self.root.mainloop()

    def refresh_list(self):
        """데이터프레임의 컬럼을 다시 읽어와 리스트박스를 갱신합니다."""
        self.listbox.delete(0, tk.END)
        self.ordered_indices = []
        for col in self.df_obj.columns:
            self.listbox.insert(tk.END, str(col))
        print(f"List updated for DataFrame: {self.df_name}")

    def on_select(self, event):
        current_sel = list(self.listbox.curselection())
        for i in current_sel:
            if i not in self.ordered_indices:
                self.ordered_indices.append(i)
        self.ordered_indices = [i for i in self.ordered_indices if i in current_sel]

    def type_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update() # [수정됨] Tkinter 클립보드 강제 동기화 (필수)
        
        # [수정됨] 현재 포커스가 Tkinter 창에 있으므로, Alt+Tab으로 이전 창(에디터)으로 돌아갑니다.
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.3) # 화면이 전환될 때까지 여유 대기시간 부여
        
        # 이전 에디터 창의 커서 위치에 붙여넣기
        pyautogui.hotkey('ctrl', 'v') 
        print(text)

    def insert_simple(self):
        if self.ordered_indices:
            cols = self.df_obj.columns
            selected_vars = [str(cols[i]) for i in self.ordered_indices]
            var_string = ", ".join(selected_vars)
            self.type_text(var_string)
            self.listbox.selection_clear(0, tk.END)
            self.ordered_indices = []

    def insert_lm(self):
        if self.ordered_indices:
            cols = self.df_obj.columns
            selected_vars = [str(cols[i]) for i in self.ordered_indices]
            
            if len(selected_vars) == 1:
                var_string = selected_vars[0]
            else:
                target = selected_vars[0]
                features = " + ".join(selected_vars[1:])
                # [수정됨] model 대신 result 사용, 끝의 .fit() 제거
                var_string = f"result = smf.ols(formula= '{target} ~ {features}', data={self.df_name} ) "
            
            self.type_text(var_string)
            self.listbox.selection_clear(0, tk.END)
            self.ordered_indices = []

def selvar(df_obj):
    frame = inspect.currentframe().f_back
    df_name = "df"
    for name, val in frame.f_locals.items():
        if val is df_obj:
            df_name = name
            break
    VariableSelector(df_obj, df_name)
