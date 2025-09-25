import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import Tk, ttk, filedialog, messagebox, StringVar, Frame, Label
from PIL import Image

SUPPORTED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.webp', '.ico', '.pcx'}

TIFF_COMPRESSION = {
    1: "None",
    2: "CCITT RLE",
    3: "CCITT T.4",
    4: "CCITT T.6",
    5: "LZW",
    6: "JPEG (old)",
    7: "JPEG",
    8: "Deflate (ZIP)",
    32773: "PackBits",
}

def human_filesize(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

def human_bpp_from_mode(mode):
    mapping = {
        '1': 1,
        'L': 8,
        'P': 8,
        'RGB': 24,
        'RGBA': 32,
        'CMYK': 32,
        'I': 32,
        'F': 32,
    }
    return mapping.get(mode, None)

def get_compression(img, path):
    fmt = (img.format or "").upper()
    if fmt == "JPEG":
        return "JPEG"
    if fmt == "PNG":
        return "DEFLATE"
    if fmt == "GIF":
        return "LZW"
    if fmt == "BMP":
        return "None"
    if fmt == "WEBP":
        return "WEBP"
    if fmt == "TIFF":
        tags = getattr(img, "tag_v2", None)
        if tags is not None:
            c = tags.get(259)
            if c is not None:
                return TIFF_COMPRESSION.get(int(c), f"TIFF #{c}")
        return "TIFF (unknown)"
    if fmt == "PCX":
        return "RLE (PCX)"
    if fmt == "ICO":
        return "None"
    return fmt or "unknown"

def get_dpi(img):
    info = img.info
    dpi = info.get('dpi')
    if dpi:
        if isinstance(dpi, (tuple, list)) and len(dpi) >= 2:
            x, y = dpi[0], dpi[1]
            if x > 0 and y > 0:
                return f"{int(x)}x{int(y)}"
        elif isinstance(dpi, (int, float)) and dpi > 0:
            d = int(dpi)
            return f"{d}x{d}"
    ppm_x = info.get('xppm') or info.get('XPixelsPerMeter')
    ppm_y = info.get('yppm') or info.get('YPixelsPerMeter')
    if ppm_x and ppm_y:
        xdpi = int(ppm_x * 0.0254)
        ydpi = int(ppm_y * 0.0254)
        return f"{xdpi}x{ydpi}"
    exif = img.getexif()
    if exif:
        xr = exif.get(282)
        yr = exif.get(283)
        if xr:
            def to_float(r):
                return float(r[0]) / float(r[1]) if isinstance(r, tuple) else float(r)
            x = to_float(xr)
            y = to_float(yr) if yr else x
            if x > 0 and y > 0:
                return f"{int(x)}x{int(y)}"
    if img.format == "BMP":
        path = getattr(img, "filename", None)
        if path and Path(path).exists():
            with open(path, 'rb') as f:
                f.seek(38)
                xppm_bytes = f.read(4)
                yppm_bytes = f.read(4)
                if len(xppm_bytes) == 4 and len(yppm_bytes) == 4:
                    xppm = int.from_bytes(xppm_bytes, 'little', signed=True)
                    yppm = int.from_bytes(yppm_bytes, 'little', signed=True)
                    if xppm > 0 and yppm > 0:
                        xdpi = int(xppm * 0.0254)
                        ydpi = int(yppm * 0.0254)
                        return f"{xdpi}x{ydpi}"
    return None

def inspect_image(path):
    path = str(path)
    with Image.open(path) as img:
        fmt = img.format
        width, height = img.size
        mode = img.mode
        bpp = human_bpp_from_mode(mode)
        dpi = get_dpi(img)
        comp = get_compression(img, path)
        return {
            'path': path,
            'name': os.path.basename(path),
            'format': fmt,
            'width': width,
            'height': height,
            'dpi': dpi,
            'mode': mode,
            'bpp': bpp,
            'compression': comp,
            'filesize': human_filesize(os.path.getsize(path)),
        }

class ImageDataApp:
    def __init__(self, root):
        self.root = root
        root.title("Image Data")
        root.geometry("1100x650")
        root.minsize(900, 500)
        root.configure(bg="#f5f7fa")
        self.setup_styles()
        self.create_widgets()
        self.files_list = []
        self.executor = None
        self.results = []
        self.stop_flag = threading.Event()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        bg = "#f5f7fa"
        fg = "#2e2e2e"
        accent = "#2196F3"
        hover = "#1976D2"
        tree_bg = "#ffffff"
        tree_fg = "#2e2e2e"
        tree_sel = "#e3f2fd"

        style.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("TButton",
                        background=accent,
                        foreground="white",
                        borderwidth=0,
                        padding=(10, 6),
                        font=("Segoe UI", 10, "bold"))
        style.map("TButton",
                  background=[('active', hover)])

        style.configure("Treeview",
                        background=tree_bg,
                        foreground=tree_fg,
                        fieldbackground=tree_bg,
                        rowheight=26,
                        font=("Consolas", 9))
        style.map("Treeview",
                  background=[('selected', tree_sel)],
                  foreground=[('selected', '#1a1a1a')])

        style.configure("Treeview.Heading",
                        background="#edf2f7",
                        foreground="#2e2e2e",
                        font=("Segoe UI", 9, "bold"),
                        padding=(4, 6))
        style.map("Treeview.Heading",
                  background=[('active', '#dde7f0')])

        style.configure("TLabel", background=bg, foreground=fg)

    def create_widgets(self):
        control_frame = Frame(self.root, bg="#f5f7fa")
        control_frame.pack(fill='x', padx=16, pady=(16, 8))
        self.path_var = StringVar(value="Не выбрано")
        path_label = Label(control_frame, textvariable=self.path_var,
                           bg="#ffffff",
                           fg="#5a5a5a",
                           font=("Consolas", 9),
                           padx=10, pady=6, anchor="w",
                           relief="solid", borderwidth=1)
        path_label.pack(side='left', fill='x', expand=True, padx=(0, 12))
        btn_frame = Frame(control_frame, bg="#f5f7fa")
        btn_frame.pack(side='right')
        self.btn_folder = ttk.Button(btn_frame, text="Папка", command=self.select_folder)
        self.btn_files = ttk.Button(btn_frame, text="Файлы", command=self.select_files)
        self.btn_start = ttk.Button(btn_frame, text="Старт", command=self.start_scan)
        self.btn_stop = ttk.Button(btn_frame, text="Стоп", command=self.stop_scan)
        for btn in [self.btn_folder, self.btn_files, self.btn_start, self.btn_stop]:
            btn.pack(side='left', padx=4)
        
        tree_frame = Frame(self.root, bg="#f5f7fa")
        tree_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        columns = ('name', 'format', 'size_px', 'dpi', 'bpp', 'compression', 'filesize')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode="browse")
        self.tree.heading('name', text='Файл')
        self.tree.heading('format', text='Формат')
        self.tree.heading('size_px', text='Размер (px)')
        self.tree.heading('dpi', text='DPI')
        self.tree.heading('bpp', text='Глубина цвета')
        self.tree.heading('compression', text='Сжатие')
        self.tree.heading('filesize', text='Размер')

        self.tree.column('name', width=220, minwidth=150, anchor='w')
        self.tree.column('format', width=80, minwidth=60, anchor='center')
        self.tree.column('size_px', width=110, minwidth=90, anchor='center')
        self.tree.column('dpi', width=80, minwidth=60, anchor='center')
        self.tree.column('bpp', width=90, minwidth=70, anchor='center')
        self.tree.column('compression', width=160, minwidth=120, anchor='center')
        self.tree.column('filesize', width=90, minwidth=70, anchor='center')

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        self.status = StringVar(value="Готово")
        self.status_label = Label(self.root, textvariable=self.status,
                                  bg="#f5f7fa",
                                  fg="#6a7a8c",
                                  font=("Segoe UI", 9),
                                  anchor='w', padx=16)
        self.status_label.pack(fill='x', side='bottom')

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.files_list = []
            for root_dir, dirs, files in os.walk(folder):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in SUPPORTED_EXT:
                        self.files_list.append(os.path.join(root_dir, f))
                    if len(self.files_list) >= 200000:
                        break
            self.status.set(f"Найдено: {len(self.files_list)} файлов")

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[
            ("Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.gif *.webp *.ico *.pcx"),
            ("All files", "*.*")
        ])
        if files:
            self.path_var.set(f"{len(files)} файлов выбрано")
            self.files_list = list(files)
            self.status.set(f"Готово к анализу: {len(self.files_list)} файлов")

    def start_scan(self):
        if not self.files_list:
            messagebox.showinfo("Нет файлов", "Сначала выберите папку или файлы")
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.results = []
        self.stop_flag.clear()
        max_workers = min(32, (os.cpu_count() or 2) * 2)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        total = len(self.files_list)
        self.status.set(f"Обработка {total} файлов...")
        for path in self.files_list:
            if self.stop_flag.is_set():
                break
            self.executor.submit(self._process_file, path)
        self.root.after(200, self._monitor)

    def _process_file(self, path):
        res = inspect_image(path)
        self.results.append(res)
        self.root.after(0, self._add_to_tree, res)

    def _add_to_tree(self, res):
        size_px = f"{res['width']}x{res['height']}"
        self.tree.insert('', 'end', values=(
            res['name'],
            res['format'] or "-",
            size_px,
            res['dpi'] or "-",
            f"{res['bpp']}" if res['bpp'] else "-",
            res['compression'] or "-",
            res['filesize'],
        ))

    def _monitor(self):
        done = len(self.results)
        total = len(self.files_list)
        self.status.set(f"Прогресс: {done}/{total} файлов")
        if self.stop_flag.is_set():
            self.status.set(f"Остановлено: обработано {done}/{total}")
            if self.executor:
                self.executor.shutdown(wait=False)
                self.executor = None
            return
        if done >= total:
            if self.executor:
                self.executor.shutdown(wait=False)
                self.executor = None
            self.status.set(f"Завершено: {done}/{total} файлов")
            return
        self.root.after(200, self._monitor)

    def stop_scan(self):
        self.stop_flag.set()
        self.status.set("Запрос на остановку...")

def main():
    root = Tk()
    root.option_add('*tearOff', False)
    app = ImageDataApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
