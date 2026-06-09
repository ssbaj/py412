def check_dependencies():
    required_pkgs = {'pandas': 'pandas', 'openpyxl': 'openpyxl', 'chardet': 'chardet', 'pyreadstat': 'pyreadstat'}
    missing = []
    for module, pkg_name in required_pkgs.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(pkg_name)
    
    if missing:
        missing_str = " ".join(missing)
        raise ImportError(f"\n[설치 필요] 다음 패키지가 없습니다. 터미널에서 실행하세요:\npip install {missing_str}")

def guess_encoding(file_path, num_bytes=10000):
    """R의 readr::guess_encoding 역할 (chardet 사용)"""
    import chardet
    try:
        with open(file_path, 'rb') as f:
            rawdata = f.read(num_bytes)
        result = chardet.detect(rawdata)
        return result['encoding'] or "Unknown"
    except Exception:
        return "Unknown"

def files22():
    check_dependencies()
    
    # 1. 파일 선택 창 (Tkinter 메인 윈도우 숨김)
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    
    filetypes = [
        ("All Files", "*.*"),
        ("Data Files", "*.xlsx *.xls *.csv *.sav *.dat *.txt")
    ]
    
    f_path = filedialog.askopenfilename(parent=root, title="Select Data File", filetypes=filetypes)
    
    if not f_path:
        print("File selection canceled.")
        root.destroy()
        return None
        
    ext = os.path.splitext(f_path)[1].lower().replace(".", "")
    supported_ext = ["xlsx", "xls", "csv", "sav", "dat", "txt"]
    
    if ext not in supported_ext:
        messagebox.showwarning("Warning", "files22 only supports xlsx, xls, csv, sav, dat, and txt files.")
        root.destroy()
        return None
        
    # 인코딩 추측
    rec_enc = "Unknown"
    if ext in ["csv", "txt"]:
        rec_enc = guess_encoding(f_path)
        # 한국어 환경에서 EUC-KR이 주로 감지되지만, pandas에서는 CP949를 사용하는 것이 호환성에 좋습니다.
        if rec_enc and rec_enc.upper() == "EUC-KR":
            rec_enc = "CP949"

    # 2. 옵션 GUI 창 띄우기
    opt_win = tk.Toplevel(root)
    opt_win.title(f"Import Options: {os.path.basename(f_path)}")
    opt_win.geometry("350x580")
    opt_win.attributes("-topmost", True)
    
    # 변수 설정
    skip_var = tk.StringVar(value="0")
    header_var = tk.IntVar(value=1)
    enc_var = tk.StringVar(value="UTF-8")
    sep_var = tk.StringVar(value=",")
    
    # [1] Number of Rows to Skip
    tk.Label(opt_win, text="1. Number of Rows to Skip", font=("Helvetica", 10, "bold")).pack(pady=(15, 2))
    tk.Entry(opt_win, textvariable=skip_var, width=10, justify="center").pack(pady=5)
    
    # [Header]
    tk.Checkbutton(opt_win, text=" Header (First Row as Names)", font=("Helvetica", 10, "bold"), variable=header_var).pack(pady=10)
    
    # [2] Select Encoding (csv, txt 전용)
    if ext in ["csv", "txt"]:
        tk.Label(opt_win, text="2. Select Encoding", font=("Helvetica", 10, "bold")).pack(pady=(10, 2))
        tk.Label(opt_win, text=f"💡 Recommended Encoding: {rec_enc}", fg="blue").pack(pady=(0, 5))
        
        enc_frame = tk.Frame(opt_win)
        tk.Radiobutton(enc_frame, text="UTF-8", variable=enc_var, value="UTF-8").pack(anchor="w")
        tk.Radiobutton(enc_frame, text="EUC-KR", variable=enc_var, value="EUC-KR").pack(anchor="w")
        tk.Radiobutton(enc_frame, text="CP949", variable=enc_var, value="CP949").pack(anchor="w")
        tk.Radiobutton(enc_frame, text="ASCII", variable=enc_var, value="ASCII").pack(anchor="w")
        enc_frame.pack(pady=5)
        
    # [3] Select Text Separator (txt 전용)
    if ext == "txt":
        tk.Label(opt_win, text="3. Select Text Separator", font=("Helvetica", 10, "bold")).pack(pady=(10, 2))
        rb_frame = tk.Frame(opt_win)
        tk.Radiobutton(rb_frame, text="Comma (,)", variable=sep_var, value=",").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Dot (.)", variable=sep_var, value=".").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Tab", variable=sep_var, value="\t").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Blank (Space)", variable=sep_var, value=" ").pack(anchor="w")
        rb_frame.pack(pady=5)

    result_data = None  # 결과를 저장할 변수
    
    def load_action():
        nonlocal result_data
        
        try:
            s_val = int(skip_var.get())
        except ValueError:
            s_val = 0
            
        h_val = bool(header_var.get())
        current_sep = sep_var.get()
        current_enc = enc_var.get()
        
        # Pandas는 header 파라미터가 0이면 첫 줄을 컬럼명으로, None이면 컬럼명 없이 데이터를 불러옵니다.
        header_arg = 0 if h_val else None
        
        try:
            if ext in ["xlsx", "xls"]:
                result_data = pd.read_excel(f_path, skiprows=s_val, header=header_arg)
            elif ext == "csv":
                result_data = pd.read_csv(f_path, skiprows=s_val, header=header_arg, encoding=current_enc)
            elif ext == "txt":
                # 공백 분리자의 경우 정규표현식 '\s+'를 사용합니다.
                use_sep = r'\s+' if current_sep == " " else current_sep
                result_data = pd.read_table(f_path, skiprows=s_val, header=header_arg, sep=use_sep, encoding=current_enc)
            elif ext == "sav":
                result_data = pd.read_spss(f_path)
                if s_val > 0:
                    result_data = result_data.iloc[s_val:].reset_index(drop=True)
            elif ext == "dat":
                # R 코드에서 haven::read_dta를 사용하므로 Python에서는 stata 로더를 매핑합니다.
                result_data = pd.read_stata(f_path)
                if s_val > 0:
                    result_data = result_data.iloc[s_val:].reset_index(drop=True)
                    
            # 헤더를 사용하지 않은 경우 V1, V2 형태로 컬럼명 할당
            if not h_val and result_data is not None:
                result_data.columns = [f"V{i+1}" for i in range(len(result_data.columns))]
                
            print(f"Successfully loaded: {os.path.basename(f_path)} | Encoding: {current_enc}")
            opt_win.destroy()
            root.quit() # GUI 대기 상태 해제
            
        except Exception as e:
            messagebox.showerror("Error loading file", f"Error: {str(e)}")

    # Load 버튼
    tk.Button(opt_win, text="🚀 Load Data", command=load_action, width=20, bg="#e1f5fe").pack(pady=25)
    
    # 윈도우 닫기 이벤트(X 버튼) 처리
    def on_closing():
        opt_win.destroy()
        root.quit()
        
    opt_win.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 창이 닫힐 때까지 코드 실행 대기
    root.mainloop()
    root.destroy()
    
    return result_data

# === 실행 예시 ===
# if __name__ == "__main__":
#     df = files22()
#     if df is not None:
#         print(df.head())