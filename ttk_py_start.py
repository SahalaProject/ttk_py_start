# coding:utf-8

"""
    Author: liyubin
    Modified: 2023-7-29
    Adapted from: https://github.com/israel-dryer/File-Search-Engine-Tk
    打包 128x128 ico： pyinstaller ttk_py_start.py -i search.ico -F -w --collect-all ttkbootstrap
"""
import json
import os
import pathlib
import platform
import time
from queue import Queue
from threading import Thread
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification


class FileSearchEngine(ttk.Frame):
    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)
        # application variables
        self.base_path = pathlib.Path().absolute().as_posix()
        self.venv_path_var = ttk.StringVar(value='')
        self.pip_package_path_var = ttk.StringVar(value='')
        self.py_path_var = ttk.StringVar(value='')
        self.start_type = ttk.StringVar(value='os.popen')
        self.select_box_text = 'os.popen'
        self.result_view = None
        self.progressbar = None
        self.theme_style = None
        self.theme_name_combobox = None
        self.theme_name = 'darkly'
        self.venv_path_combobox = None
        self.venv_path_var_list = []
        self.py_path_combobox = None
        self.py_path_var_list = []
        self.sub_close_py_name = ''

        self.setup_()

        # header and labelframe option container
        option_text = "选择运行.py"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_theme()
        self.create_row_venv_path()
        self.create_row_pip_install_path()
        self.create_row_py()
        self.create_row_type()
        self.create_results_view()
        self.create_progressbar()

        self.teardown_()

    def create_theme(self):
        self.theme_style = ttk.Style()
        self.theme_style.theme_use(self.theme_name)  # 本地主题

    def create_row_venv_path(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)

        path_lbl = ttk.Label(path_row, text="venv路径", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))

        self.venv_path_combobox = ttk.Combobox(path_row, values=self.venv_path_var_list, textvariable=self.venv_path_var)
        self.venv_path_combobox.pack(side=LEFT, fill=X, expand=YES, padx=5)

        browse_btn = ttk.Button(
            master=path_row,
            text="浏览",
            command=self.on_browse_venv,
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

        create_venv_btn = ttk.Button(
            master=path_row,
            text="创建",
            command=self.on_create_venv,
            bootstyle=INFO,
            width=8
        )
        create_venv_btn.pack(side=LEFT, padx=5)

    def create_row_pip_install_path(self):
        pip_path_row = ttk.Frame(self.option_lf)
        pip_path_row.pack(fill=X, expand=YES, pady=15)

        pip_path_lbl = ttk.Label(pip_path_row, text="依赖安装", width=8)
        pip_path_lbl.pack(side=LEFT, padx=(15, 0))

        path_ent = ttk.Entry(pip_path_row, textvariable=self.pip_package_path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)

        browse_btn = ttk.Button(
            master=pip_path_row,
            text="浏览",
            command=self.on_browse_pip_package,
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

        create_venv_btn = ttk.Button(
            master=pip_path_row,
            text="安装",
            command=self.on_pip_install_package,
            bootstyle=INFO,
            width=8
        )
        create_venv_btn.pack(side=LEFT, padx=5)

    def create_row_py(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES, pady=0)

        path_lbl = ttk.Label(path_row, text=".py文件", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))

        self.py_path_combobox = ttk.Combobox(path_row, values=self.py_path_var_list, textvariable=self.py_path_var)
        self.py_path_combobox.pack(side=LEFT, fill=X, expand=YES, padx=5)

        browse_btn = ttk.Button(
            master=path_row,
            text="浏览",
            command=self.on_browse_py_path,
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

        search_btn = ttk.Button(
            master=path_row,
            text="运行",
            command=self.on_run_py,
            bootstyle=INFO,
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)

    def create_row_type(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="启动方式", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row,
            text="os.popen",
            variable=self.start_type,
            value="os.popen"
        )
        contains_opt.pack(side=LEFT)
        contains_opt.invoke()

        startswith_opt = ttk.Radiobutton(
            master=type_row,
            text="os.system start",
            variable=self.start_type,
            value="os.system start"
        )
        startswith_opt.pack(side=LEFT, padx=15)

        # base theme
        self.theme_name_combobox = ttk.Combobox(type_row, values=ttk.Style().theme_names(), width=8)
        self.theme_name_combobox.insert(END, self.theme_name)
        self.theme_name_combobox.pack(side=LEFT, pady=5)
        self.theme_name_combobox.bind("<<ComboboxSelected>>", self.change_base_theme)

        close_btn = ttk.Button(
            master=type_row,
            text="停止py",
            command=self.on_sub_close,
            bootstyle=DANGER,
            width=8
        )
        close_btn.pack(side=RIGHT, padx=5)

        clear_btn = ttk.Button(
            master=type_row,
            text="清空",
            command=self.on_clear,
            bootstyle=DANGER,
            width=8
        )
        clear_btn.pack(side=RIGHT, padx=5)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        container = ttk.Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=YES, padx=0)
        # text widget
        self.result_view = ttk.ScrolledText(master=container, wrap="none")
        self.result_view.pack(side=TOP, anchor=NW, pady=5, fill=BOTH, expand=YES)
        self.result_view.insert(END, '日志\n')

    def create_progressbar(self):
        self.progressbar = ttk.Progressbar(
            master=self,
            mode=INDETERMINATE,
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

    def on_browse_venv(self):
        """Callback for directory browse"""
        path = filedialog.askdirectory(title="Browse directory")
        if path:
            self.venv_path_var.set(path)

    def on_create_venv(self):
        path = filedialog.askdirectory(title="Browse directory")
        if path:
            self.os_popen('virtualenv {}/venv'.format(path), '')
            self.venv_path_var.set(path)

    def on_browse_pip_package(self):
        path = filedialog.askopenfilename(title="Browse directory")
        if path:
            self.pip_package_path_var.set(path)

    def on_pip_install_package(self):
        venv_path = self.venv_path_var.get()
        package_ = self.pip_package_path_var.get()
        cmd_venv = self.get_venv_cmd(venv_path)
        if not (package_ and cmd_venv):
            self.insert_row('请选择依赖包或虚拟环境\n')
        if package_.endswith('txt'):
            pip_cmd = 'pip install -r {}'.format(package_)
        else:
            pip_cmd = 'pip install {}'.format(package_)
        self.os_popen(cmd_venv + '\n' + pip_cmd + '\n' + 'pip list', '')

    def on_browse_py_path(self):
        path = filedialog.askopenfilename(title="Browse directory")
        if path:
            self.py_path_var.set(path)

    def on_run_py(self):
        """Search for a term based on the search type"""
        venv_path = self.venv_path_var.get()
        py_path = self.py_path_var.get()
        start_type = self.start_type.get()

        if py_path == '' or not py_path.endswith('.py'):
            self.insert_row('请选择.py\n')
            return

        Thread(target=self.start_py, args=(venv_path, py_path, start_type), daemon=True).start()
        self.progressbar.start(10)

    def insert_row(self, txt):
        """Insert new row in tree search results"""
        try:
            self.result_view.insert(END, txt)
            self.result_view.yview_moveto(1)  # 自动滚动到最下
        except OSError:
            return

    def start_py(self, venv_path, py_file_path, start_type):
        """Recursively search directory for matching files"""
        self.set_start_button(True)
        self.set_venv_py_combobox_()

        cmd_venv = self.get_venv_cmd(venv_path)
        py_file, py_path = self.get_py_file_and_path(py_file_path)
        if platform.platform().lower() == 'windows':
            if start_type == 'os.popen':
                cmd_py = 'python {}'.format(py_file)
            else:
                cmd_py = 'start python {}'.format(py_file)
        else:
            cmd_py = 'python3 {}'.format(py_file)

        if cmd_venv:
            cmd_ = cmd_venv + '\n' + cmd_py
        else:
            cmd_ = cmd_py

        if start_type == 'os.popen':
            self.os_popen(cmd_, py_path)
        else:
            self.os_system(cmd_, py_path)

    def os_popen(self, cmd_, py_path):
        self.insert_row('cmd: ' + cmd_ + '\n')
        os.chdir(py_path)
        sup = os.popen(cmd_)
        os.chdir(self.base_path)
        while True:
            try:
                select_flag, now_select_py = self.is_select_py_is_run(py_path, cmd_)
                if select_flag:
                    line = sup.readline().encode('utf-8')
                    if line:
                        self.insert_row(line)
                    else:
                        break
                    if now_select_py in self.sub_close_py_name:
                        self.sub_close_py_name = ''
                        break
                else:
                    time.sleep(2)
            except Exception as ex:
                self.insert_row(str(ex) + '\n')
        self.set_start_button(False)
        self.progressbar.stop()
        self.show_toast_notification('运行结束')

    def is_select_py_is_run(self, run_py_path, run_cmd_):
        """日志只显示选中的py，提升性能"""
        now_select_py = self.py_path_var.get()
        py_file, py_path = self.get_py_file_and_path(now_select_py)
        if isinstance(now_select_py, str) and py_file in run_cmd_ and py_path in run_py_path:
            return True, now_select_py

    def on_sub_close(self):
        """close popen"""
        self.sub_close_py_name = self.py_path_var.get()

    def os_system(self, cmd_, py_path):
        self.insert_row('cmd: ' + cmd_ + '\n')
        os.chdir(py_path)
        os.system(cmd_)
        os.chdir(self.base_path)
        self.set_start_button(False)
        self.progressbar.stop()

    @staticmethod
    def get_venv_cmd(venv_path):
        if venv_path:
            if platform.platform().lower() == 'windows':
                cmd_venv = '{}/Scripts/activate'.format(venv_path)
            else:
                cmd_venv = 'source {}/bin/activate'.format(venv_path)
        else:
            cmd_venv = None
        return cmd_venv

    @staticmethod
    def get_py_file_and_path(py_file_path):
        py_file_path = py_file_path.replace('\\', '/').split('/')
        py_file = py_file_path[len(py_file_path) - 1:][0]
        py_file_path.remove(py_file)
        py_path = '/'.join(py_file_path)
        return py_file, py_path

    @staticmethod
    def set_start_button(state=False):
        """Set searching status"""
        FileSearchEngine.searching = state

    def set_venv_py_combobox_(self):
        self.venv_path_var_list.append(self.venv_path_combobox.get())
        self.venv_path_var_list = list(set(self.venv_path_var_list))
        self.venv_path_combobox['values'] = self.venv_path_var_list
        
        self.py_path_var_list.append(self.py_path_combobox.get())
        self.py_path_var_list = list(set(self.py_path_var_list))
        self.py_path_combobox['values'] = self.py_path_var_list
        self.write_venv_py_path_to_json()

    def write_venv_py_path_to_json(self):
        """可选项本地化"""
        with open('tk_db.json', 'w', encoding='utf-8')as fp:
            json.dump({'venv_path_var_list': self.venv_path_var_list,
                       'py_path_var_list': self.py_path_var_list,
                       'theme_name': self.theme_name_combobox.get(),
                       }, fp)

    def read_venv_py_path_to_json(self, method):
        """启动时加载"""
        if method == 'setup_':
            try:
                with open('tk_db.json', 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
            except Exception as e:
                with open('ttk_error.txt', 'w')as fp:
                    fp.write(str(e))
                data = {}
            self.venv_path_var_list = data.get('venv_path_var_list', [])
            self.py_path_var_list = data.get('py_path_var_list', [])
            self.theme_name = data.get('theme_name', 'darkly')

        if method == 'teardown_':
            self.venv_path_combobox['values'] = self.venv_path_var_list
            self.py_path_combobox['values'] = self.py_path_var_list

    def setup_(self):
        """ttk初始化前"""
        self.read_venv_py_path_to_json('setup_')

    def teardown_(self):
        """ttk初始化后"""
        self.read_venv_py_path_to_json('teardown_')

    def change_base_theme(self, *_):
        """Sets the initial colors used in the color configuration"""
        theme_name = self.theme_name_combobox.get()
        self.write_venv_py_path_to_json()
        self.theme_style.theme_use(theme_name)

    def on_clear(self):
        """重置"""
        self.result_view.delete(1.0, END)

    @staticmethod
    def show_toast_notification(msg):
        """系统提示"""
        toast = ToastNotification(
            title="消息提示",
            message=msg,
            duration=3000,
        )
        toast.show_toast()


if __name__ == '__main__':
    app = ttk.Window("python启动器-liyubin", themename='journal')  # journal
    FileSearchEngine(app)
    app.mainloop()
