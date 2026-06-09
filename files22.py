# conda install -c conda-forge pyreadstat
# pip install pyreadstat

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import importlib

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
        raise ImportError(f"\n[?¤ì¹˜ ?„ìš”] ?¤ìŒ ?¨í‚¤ì§€ê°€ ?†ìŠµ?ˆë‹¤. ?°ë??ì—???¤í–‰?˜ì„¸??\npip install {missing_str}")

def guess_encoding(file_path, num_bytes=10000):
    """R??readr::guess_encoding ??•  (chardet ?¬ìš©)"""
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
    
    # 1. ?Œì¼ ? íƒ ì°?(Tkinter ë©”ì¸ ?ˆë„???¨ê?)
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
        
    # ?¸ì½”??ì¶”ì¸¡
    rec_enc = "Unknown"
    if ext in ["csv", "txt"]:
        rec_enc = guess_encoding(f_path)
        # ?œêµ­???˜ê²½?ì„œ EUC-KR??ì£¼ë¡œ ê°ì??˜ì?ë§? pandas?ì„œ??CP949ë¥??¬ìš©?˜ëŠ” ê²ƒì´ ?¸í™˜?±ì— ì¢‹ìŠµ?ˆë‹¤.
        if rec_enc and rec_enc.upper() == "EUC-KR":
            rec_enc = "CP949"

    # 2. ?µì…˜ GUI ì°??„ìš°ê¸?
    opt_win = tk.Toplevel(root)
    opt_win.title(f"Import Options: {os.path.basename(f_path)}")
    opt_win.geometry("350x580")
    opt_win.attributes("-topmost", True)
    
    # ë³€???¤ì •
    skip_var = tk.StringVar(value="0")
    header_var = tk.IntVar(value=1)
    enc_var = tk.StringVar(value="UTF-8")
    sep_var = tk.StringVar(value=",")
    
    # [1] Number of Rows to Skip
    tk.Label(opt_win, text="1. Number of Rows to Skip", font=("Helvetica", 10, "bold")).pack(pady=(15, 2))
    tk.Entry(opt_win, textvariable=skip_var, width=10, justify="center").pack(pady=5)
    
    # [Header]
    tk.Checkbutton(opt_win, text=" Header (First Row as Names)", font=("Helvetica", 10, "bold"), variable=header_var).pack(pady=10)
    
    # [2] Select Encoding (csv, txt ?„ìš©)
    if ext in ["csv", "txt"]:
        tk.Label(opt_win, text="2. Select Encoding", font=("Helvetica", 10, "bold")).pack(pady=(10, 2))
        tk.Label(opt_win, text=f"?’¡ Recommended Encoding: {rec_enc}", fg="blue").pack(pady=(0, 5))
        
        enc_frame = tk.Frame(opt_win)
        tk.Radiobutton(enc_frame, text="UTF-8", variable=enc_var, value="UTF-8").pack(anchor="w")
        tk.Radiobutton(enc_frame, text="EUC-KR", variable=enc_var, value="EUC-KR").pack(anchor="w")
        tk.Radiobutton(enc_frame, text="CP949", variable=enc_var, value="CP949").pack(anchor="w")
        tk.Radiobutton(enc_frame, text="ASCII", variable=enc_var, value="ASCII").pack(anchor="w")
        enc_frame.pack(pady=5)
        
    # [3] Select Text Separator (txt ?„ìš©)
    if ext == "txt":
        tk.Label(opt_win, text="3. Select Text Separator", font=("Helvetica", 10, "bold")).pack(pady=(10, 2))
        rb_frame = tk.Frame(opt_win)
        tk.Radiobutton(rb_frame, text="Comma (,)", variable=sep_var, value=",").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Dot (.)", variable=sep_var, value=".").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Tab", variable=sep_var, value="\t").pack(anchor="w")
        tk.Radiobutton(rb_frame, text="Blank (Space)", variable=sep_var, value=" ").pack(anchor="w")
        rb_frame.pack(pady=5)

    result_data = None  # ê²°ê³¼ë¥??€?¥í•  ë³€??
    
    def load_action():
        nonlocal result_data
        
        try:
            s_val = int(skip_var.get())
        except ValueError:
            s_val = 0
            
        h_val = bool(header_var.get())
        current_sep = sep_var.get()
        current_enc = enc_var.get()
        
        # Pandas??header ?Œë¼ë¯¸í„°ê°€ 0?´ë©´ ì²?ì¤„ì„ ì»¬ëŸ¼ëª…ìœ¼ë¡? None?´ë©´ ì»¬ëŸ¼ëª??†ì´ ?°ì´?°ë? ë¶ˆëŸ¬?µë‹ˆ??
        header_arg = 0 if h_val else None
        
        try:
            if ext in ["xlsx", "xls"]:
                result_data = pd.read_excel(f_path, skiprows=s_val, header=header_arg)
            elif ext == "csv":
                result_data = pd.read_csv(f_path, skiprows=s_val, header=header_arg, encoding=current_enc)
            elif ext == "txt":
                # ê³µë°± ë¶„ë¦¬?ì˜ ê²½ìš° ?•ê·œ?œí˜„??'\s+'ë¥??¬ìš©?©ë‹ˆ??
                use_sep = r'\s+' if current_sep == " " else current_sep
                result_data = pd.read_table(f_path, skiprows=s_val, header=header_arg, sep=use_sep, encoding=current_enc)
            elif ext == "sav":
                result_data = pd.read_spss(f_path)
                if s_val > 0:
                    result_data = result_data.iloc[s_val:].reset_index(drop=True)
            elif ext == "dat":
                # R ì½”ë“œ?ì„œ haven::read_dtaë¥??¬ìš©?˜ë?ë¡?Python?ì„œ??stata ë¡œë”ë¥?ë§¤í•‘?©ë‹ˆ??
                result_data = pd.read_stata(f_path)
                if s_val > 0:
                    result_data = result_data.iloc[s_val:].reset_index(drop=True)
                    
            # ?¤ë”ë¥??¬ìš©?˜ì? ?Šì? ê²½ìš° V1, V2 ?•íƒœë¡?ì»¬ëŸ¼ëª?? ë‹¹
            if not h_val and result_data is not None:
                result_data.columns = [f"V{i+1}" for i in range(len(result_data.columns))]
                
            print(f"Successfully loaded: {os.path.basename(f_path)} | Encoding: {current_enc}")
            opt_win.destroy()
            root.quit() # GUI ?€ê¸??íƒœ ?´ì œ
            
        except Exception as e:
            messagebox.showerror("Error loading file", f"Error: {str(e)}")

    # Load ë²„íŠ¼
    tk.Button(opt_win, text="?? Load Data", command=load_action, width=20, bg="#e1f5fe").pack(pady=25)
    
    # ?ˆë„???«ê¸° ?´ë²¤??X ë²„íŠ¼) ì²˜ë¦¬
    def on_closing():
        opt_win.destroy()
        root.quit()
        
    opt_win.protocol("WM_DELETE_WINDOW", on_closing)
    
    # ì°½ì´ ?«í ?Œê¹Œì§€ ì½”ë“œ ?¤í–‰ ?€ê¸?
    root.mainloop()
    root.destroy()
    
    return result_data

# === ?¤í–‰ ?ˆì‹œ ===
# if __name__ == "__main__":
#     df = files22()
#     if df is not None:
#         print(df.head())