import tkinter as tk
from tkinter import ttk # ttk 模块提供了一些样式更好的控件
from tkinter import messagebox # 用于显示简单的消息框

# 假设你的后端逻辑在 backend.py 文件中
# 你需要确保 backend.py 中的 DB_CONFIG 配置正确
# 并且相关函数 (get_all_students, add_student, update_student, delete_student,
# get_all_courses, add_course, update_course, delete_course,
# select_course, drop_course, get_student_selected_courses, record_grade,
# get_grade_audit_logs) 存在且能正常工作
try:
    import backend # 导入我们之前写的后端逻辑
except ImportError:
    messagebox.showerror("错误", "无法导入 backend.py。\n请确保该文件存在于同一目录下且无语法错误。")
    exit()
except Exception as e:
    messagebox.showerror("后端导入错误", f"导入 backend.py 时发生错误: {e}")
    exit()


class StudentCourseApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("学生选课管理系统") # 窗口标题
        self.root.geometry("1000x800") # 调整窗口初始大小

        # --- 创建主 Notebook (选项卡) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- 创建学生管理选项卡 ---
        self.student_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.student_tab, text='学生管理')
        self.create_student_widgets()

        # --- 创建课程管理选项卡 ---
        self.course_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.course_tab, text='课程管理')
        self.create_course_widgets()

        # --- 创建选课管理选项卡 ---
        self.selection_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.selection_tab, text='选课管理')
        self.create_selection_widgets()

        # --- 创建成绩审计日志选项卡 ---
        self.audit_log_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.audit_log_tab, text='成绩审计日志')
        self.create_audit_log_widgets()
        
        # --- 初始加载数据 ---
        self.load_students()
        self.load_courses()
        self.populate_selection_student_combobox() # 填充选课管理中的学生下拉框
        self.populate_selection_course_combobox()  # 填充选课管理中的课程下拉框
        self.load_grade_audit_logs() # 初始加载审计日志


    #-------------------------------------------------------------------
    # 学生管理相关 Widgets 和方法
    #-------------------------------------------------------------------
    def create_student_widgets(self):
        # --- 操作按钮区域 (学生) ---
        student_action_frame = ttk.Frame(self.student_tab, padding="10")
        student_action_frame.pack(fill=tk.X, pady=(0,10))

        self.add_student_button = ttk.Button(student_action_frame, text="添加学生", command=self.open_add_student_window)
        self.add_student_button.pack(side=tk.LEFT, padx=5)

        self.update_student_button = ttk.Button(student_action_frame, text="修改选中学生", command=self.open_update_student_window)
        self.update_student_button.pack(side=tk.LEFT, padx=5)

        self.delete_student_button = ttk.Button(student_action_frame, text="删除选中学生", command=self.delete_selected_student)
        self.delete_student_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_students_button = ttk.Button(student_action_frame, text="刷新列表", command=self.load_students)
        self.refresh_students_button.pack(side=tk.LEFT, padx=5)

        # --- 学生列表显示区域 ---
        student_list_frame = ttk.LabelFrame(self.student_tab, text="学生列表", padding="10")
        student_list_frame.pack(fill=tk.BOTH, expand=True)

        self.student_tree = ttk.Treeview(student_list_frame, columns=("id", "name", "gender", "year", "email"), show="headings")
        self.student_tree.heading("id", text="ID")
        self.student_tree.heading("name", text="姓名")
        self.student_tree.heading("gender", text="性别")
        self.student_tree.heading("year", text="入学年份")
        self.student_tree.heading("email", text="邮箱")

        self.student_tree.column("id", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.student_tree.column("name", width=150, stretch=tk.YES)
        self.student_tree.column("gender", width=80, anchor=tk.CENTER, stretch=tk.NO)
        self.student_tree.column("year", width=100, anchor=tk.CENTER, stretch=tk.NO)
        self.student_tree.column("email", width=250, stretch=tk.YES)

        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        student_scrollbar = ttk.Scrollbar(student_list_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscroll=student_scrollbar.set)
        student_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.student_tree.bind("<Double-1>", self.on_student_double_click)

    def on_student_double_click(self, event):
        if self.student_tree.selection():
            self.open_update_student_window()

    def load_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        try:
            students_data = backend.get_all_students()
            if students_data:
                for student in students_data:
                    self.student_tree.insert("", tk.END, values=(
                        student.get('student_id', ''), student.get('student_name', ''),
                        student.get('student_gender', ''), student.get('enrollment_year', ''),
                        student.get('email', '')
                    ))
            self.populate_selection_student_combobox() 
        except AttributeError as ae:
             messagebox.showerror("后端函数错误", f"调用 backend.py 中的函数时出错: {ae}\n请确保 get_all_students 函数已正确定义。")
        except Exception as e:
            messagebox.showerror("加载学生数据失败", f"发生错误: {e}\n请确保数据库连接正常且backend.py中的函数无误。")

    def open_add_student_window(self):
        self.add_student_win = tk.Toplevel(self.root)
        self.add_student_win.title("添加新学生")
        self.add_student_win.geometry("350x250")
        self.add_student_win.transient(self.root) 
        self.add_student_win.grab_set() 

        form_frame = ttk.Frame(self.add_student_win, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(form_frame, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.add_s_name_entry = ttk.Entry(form_frame, width=30)
        self.add_s_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="性别:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.add_s_gender_combobox = ttk.Combobox(form_frame, values=["男", "女", "其他"], state="readonly", width=27)
        self.add_s_gender_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.add_s_gender_combobox.set("男") 

        ttk.Label(form_frame, text="入学年份:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.add_s_year_entry = ttk.Entry(form_frame, width=30)
        self.add_s_year_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="邮箱:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.add_s_email_entry = ttk.Entry(form_frame, width=30)
        self.add_s_email_entry.grid(row=3, column=1, padx=5, pady=5)

        save_button = ttk.Button(form_frame, text="保存", command=self.save_new_student)
        save_button.grid(row=4, column=0, columnspan=2, pady=15)
        self.add_s_name_entry.focus_set() 

    def save_new_student(self):
        name = self.add_s_name_entry.get().strip()
        gender = self.add_s_gender_combobox.get()
        year_str = self.add_s_year_entry.get().strip()
        email = self.add_s_email_entry.get().strip()

        if not name:
            messagebox.showwarning("输入错误", "学生姓名不能为空！", parent=self.add_student_win)
            return
        if not year_str.isdigit() or not (1900 <= int(year_str) <= 2100):
            messagebox.showwarning("输入错误", "请输入有效的入学年份 (例如 2023)！", parent=self.add_student_win)
            return
        year = int(year_str)
        try:
            if backend.add_student(name, gender, year, email):
                messagebox.showinfo("成功", "学生添加成功！", parent=self.add_student_win)
                self.add_student_win.destroy()
                self.load_students() 
            else:
                messagebox.showerror("失败", "添加学生失败，可能是邮箱重复或数据库错误。", parent=self.add_student_win)
        except AttributeError as ae:
            messagebox.showerror("后端函数错误", f"调用 backend.add_student 时出错: {ae}\n请确保该函数已正确定义。", parent=self.add_student_win)
        except Exception as e:
            messagebox.showerror("操作失败", f"添加学生时发生错误: {e}", parent=self.add_student_win)

    def open_update_student_window(self):
        selected_item = self.student_tree.focus() 
        if not selected_item:
            messagebox.showwarning("操作无效", "请先在列表中选择一个学生进行修改。")
            return
        student_data = self.student_tree.item(selected_item, "values")
        student_id, current_name, current_gender, current_year, current_email = student_data

        self.update_student_win = tk.Toplevel(self.root)
        self.update_student_win.title("修改学生信息")
        self.update_student_win.geometry("380x280")
        self.update_student_win.transient(self.root)
        self.update_student_win.grab_set()

        form_frame = ttk.Frame(self.update_student_win, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(form_frame, text=f"学生ID: {student_id}").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.update_s_id_hidden = student_id 

        ttk.Label(form_frame, text="姓名:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.update_s_name_entry = ttk.Entry(form_frame, width=30)
        self.update_s_name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.update_s_name_entry.insert(0, current_name)

        ttk.Label(form_frame, text="性别:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.update_s_gender_combobox = ttk.Combobox(form_frame, values=["男", "女", "其他"], state="readonly", width=27)
        self.update_s_gender_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.update_s_gender_combobox.set(current_gender)

        ttk.Label(form_frame, text="入学年份:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.update_s_year_entry = ttk.Entry(form_frame, width=30)
        self.update_s_year_entry.grid(row=3, column=1, padx=5, pady=5)
        self.update_s_year_entry.insert(0, current_year)

        ttk.Label(form_frame, text="邮箱:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.update_s_email_entry = ttk.Entry(form_frame, width=30)
        self.update_s_email_entry.grid(row=4, column=1, padx=5, pady=5)
        self.update_s_email_entry.insert(0, current_email)

        update_button = ttk.Button(form_frame, text="更新", command=self.save_updated_student)
        update_button.grid(row=5, column=0, columnspan=2, pady=15)
        self.update_s_name_entry.focus_set()
        self.update_s_name_entry.selection_range(0, tk.END)

    def save_updated_student(self):
        student_id = self.update_s_id_hidden 
        name = self.update_s_name_entry.get().strip()
        gender = self.update_s_gender_combobox.get()
        year_str = self.update_s_year_entry.get().strip()
        email = self.update_s_email_entry.get().strip()

        if not name:
            messagebox.showwarning("输入错误", "学生姓名不能为空！", parent=self.update_student_win)
            return
        if not year_str.isdigit() or not (1900 <= int(year_str) <= 2100):
            messagebox.showwarning("输入错误", "请输入有效的入学年份 (例如 2023)！", parent=self.update_student_win)
            return
        year = int(year_str)
        try:
            if backend.update_student(student_id, name, gender, year, email):
                messagebox.showinfo("成功", "学生信息更新成功！", parent=self.update_student_win)
                self.update_student_win.destroy()
                self.load_students() 
            else:
                messagebox.showerror("失败", "更新学生信息失败，可能是邮箱重复或数据库错误。", parent=self.update_student_win)
        except AttributeError:
             messagebox.showerror("后端函数错误", "backend.py 中缺少 update_student 函数。\n请确保该函数已正确定义以更新学生所有信息。", parent=self.update_student_win)
        except Exception as e:
            messagebox.showerror("操作失败", f"更新学生时发生错误: {e}", parent=self.update_student_win)

    def delete_selected_student(self):
        selected_item = self.student_tree.focus()
        if not selected_item:
            messagebox.showwarning("操作无效", "请先在列表中选择一个学生进行删除。")
            return
        student_data = self.student_tree.item(selected_item, "values")
        student_id, student_name = student_data[0], student_data[1]
        if messagebox.askyesno("确认删除", f"您确定要删除学生 '{student_name}' (ID: {student_id}) 吗？\n此操作将同时删除该学生的所有选课记录。"):
            try:
                if backend.delete_student(student_id):
                    messagebox.showinfo("成功", f"学生 '{student_name}' 删除成功！")
                    self.load_students() 
                else:
                    messagebox.showerror("失败", f"删除学生 '{student_name}' 失败。")
            except AttributeError as ae:
                messagebox.showerror("后端函数错误", f"调用 backend.delete_student 时出错: {ae}\n请确保该函数已正确定义。")
            except Exception as e:
                 messagebox.showerror("操作失败", f"删除学生时发生错误: {e}")

    #-------------------------------------------------------------------
    # 课程管理相关 Widgets 和方法
    #-------------------------------------------------------------------
    def create_course_widgets(self):
        course_action_frame = ttk.Frame(self.course_tab, padding="10")
        course_action_frame.pack(fill=tk.X, pady=(0,10))
        self.add_course_button = ttk.Button(course_action_frame, text="添加课程", command=self.open_add_course_window)
        self.add_course_button.pack(side=tk.LEFT, padx=5)
        self.update_course_button = ttk.Button(course_action_frame, text="修改选中课程", command=self.open_update_course_window)
        self.update_course_button.pack(side=tk.LEFT, padx=5)
        self.delete_course_button = ttk.Button(course_action_frame, text="删除选中课程", command=self.delete_selected_course)
        self.delete_course_button.pack(side=tk.LEFT, padx=5)
        self.refresh_courses_button = ttk.Button(course_action_frame, text="刷新列表", command=self.load_courses)
        self.refresh_courses_button.pack(side=tk.LEFT, padx=5)

        course_list_frame = ttk.LabelFrame(self.course_tab, text="课程列表", padding="10")
        course_list_frame.pack(fill=tk.BOTH, expand=True)
        self.course_tree = ttk.Treeview(course_list_frame, columns=("id", "name", "teacher", "credits", "department", "enroll_count"), show="headings")
        self.course_tree.heading("id", text="ID")
        self.course_tree.heading("name", text="课程名称")
        self.course_tree.heading("teacher", text="教师")
        self.course_tree.heading("credits", text="学分")
        self.course_tree.heading("department", text="开课院系")
        self.course_tree.heading("enroll_count", text="选课人数")
        self.course_tree.column("id", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.course_tree.column("name", width=200, stretch=tk.YES)
        self.course_tree.column("teacher", width=100, stretch=tk.NO)
        self.course_tree.column("credits", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.course_tree.column("department", width=150, stretch=tk.NO)
        self.course_tree.column("enroll_count", width=80, anchor=tk.CENTER, stretch=tk.NO)
        self.course_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        course_scrollbar = ttk.Scrollbar(course_list_frame, orient=tk.VERTICAL, command=self.course_tree.yview)
        self.course_tree.configure(yscroll=course_scrollbar.set)
        course_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.course_tree.bind("<Double-1>", self.on_course_double_click)

    def on_course_double_click(self, event):
        if self.course_tree.selection():
            self.open_update_course_window()

    def load_courses(self):
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        try:
            courses_data = backend.get_all_courses()
            if courses_data:
                for course in courses_data:
                    self.course_tree.insert("", tk.END, values=(
                        course.get('course_id', ''), course.get('course_name', ''),
                        course.get('teacher_name', ''), course.get('credits', ''),
                        course.get('department', ''), course.get('enrollment_count', 0)
                    ))
            self.populate_selection_course_combobox() 
        except AttributeError as ae:
             messagebox.showerror("后端函数错误", f"调用 backend.py 中的函数时出错: {ae}\n请确保 get_all_courses 函数已正确定义。")
        except Exception as e:
            messagebox.showerror("加载课程数据失败", f"发生错误: {e}\n请确保数据库连接正常且backend.py中的函数无误。")
    
    def open_add_course_window(self):
        self.add_course_win = tk.Toplevel(self.root)
        self.add_course_win.title("添加新课程")
        self.add_course_win.geometry("380x280")
        self.add_course_win.transient(self.root)
        self.add_course_win.grab_set()
        form_frame = ttk.Frame(self.add_course_win, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(form_frame, text="课程名称:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.add_c_name_entry = ttk.Entry(form_frame, width=30)
        self.add_c_name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="教师名称:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.add_c_teacher_entry = ttk.Entry(form_frame, width=30)
        self.add_c_teacher_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="学分:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.add_c_credits_entry = ttk.Entry(form_frame, width=30)
        self.add_c_credits_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="开课院系:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.add_c_department_entry = ttk.Entry(form_frame, width=30)
        self.add_c_department_entry.grid(row=3, column=1, padx=5, pady=5)
        save_button = ttk.Button(form_frame, text="保存", command=self.save_new_course)
        save_button.grid(row=4, column=0, columnspan=2, pady=15)
        self.add_c_name_entry.focus_set()

    def save_new_course(self):
        name = self.add_c_name_entry.get().strip()
        teacher = self.add_c_teacher_entry.get().strip()
        credits_str = self.add_c_credits_entry.get().strip()
        department = self.add_c_department_entry.get().strip()
        if not name:
            messagebox.showwarning("输入错误", "课程名称不能为空！", parent=self.add_course_win)
            return
        if not credits_str.isdigit() or int(credits_str) < 0:
            messagebox.showwarning("输入错误", "学分必须是非负整数！", parent=self.add_course_win)
            return
        credits = int(credits_str)
        try:
            if backend.add_course(name, teacher, credits, department):
                messagebox.showinfo("成功", "课程添加成功！", parent=self.add_course_win)
                self.add_course_win.destroy()
                self.load_courses() 
            else:
                messagebox.showerror("失败", "添加课程失败，可能是课程名称重复或数据库错误。", parent=self.add_course_win)
        except AttributeError as ae:
            messagebox.showerror("后端函数错误", f"调用 backend.add_course 时出错: {ae}\n请确保该函数已正确定义。", parent=self.add_course_win)
        except Exception as e:
            messagebox.showerror("操作失败", f"添加课程时发生错误: {e}", parent=self.add_course_win)

    def open_update_course_window(self):
        selected_item = self.course_tree.focus()
        if not selected_item:
            messagebox.showwarning("操作无效", "请先在列表中选择一个课程进行修改。")
            return
        course_data = self.course_tree.item(selected_item, "values")
        course_id, current_name, current_teacher, current_credits, current_department, _ = course_data
        self.update_course_win = tk.Toplevel(self.root)
        self.update_course_win.title("修改课程信息")
        self.update_course_win.geometry("380x300")
        self.update_course_win.transient(self.root)
        self.update_course_win.grab_set()
        form_frame = ttk.Frame(self.update_course_win, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(form_frame, text=f"课程ID: {course_id}").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.update_c_id_hidden = course_id
        ttk.Label(form_frame, text="课程名称:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.update_c_name_entry = ttk.Entry(form_frame, width=30)
        self.update_c_name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.update_c_name_entry.insert(0, current_name)
        ttk.Label(form_frame, text="教师名称:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.update_c_teacher_entry = ttk.Entry(form_frame, width=30)
        self.update_c_teacher_entry.grid(row=2, column=1, padx=5, pady=5)
        self.update_c_teacher_entry.insert(0, current_teacher)
        ttk.Label(form_frame, text="学分:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.update_c_credits_entry = ttk.Entry(form_frame, width=30)
        self.update_c_credits_entry.grid(row=3, column=1, padx=5, pady=5)
        self.update_c_credits_entry.insert(0, str(current_credits))
        ttk.Label(form_frame, text="开课院系:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.update_c_department_entry = ttk.Entry(form_frame, width=30)
        self.update_c_department_entry.grid(row=4, column=1, padx=5, pady=5)
        self.update_c_department_entry.insert(0, current_department)
        update_button = ttk.Button(form_frame, text="更新", command=self.save_updated_course)
        update_button.grid(row=5, column=0, columnspan=2, pady=15)
        self.update_c_name_entry.focus_set()
        self.update_c_name_entry.selection_range(0, tk.END)

    def save_updated_course(self):
        course_id = self.update_c_id_hidden
        name = self.update_c_name_entry.get().strip()
        teacher = self.update_c_teacher_entry.get().strip()
        credits_str = self.update_c_credits_entry.get().strip()
        department = self.update_c_department_entry.get().strip()
        if not name:
            messagebox.showwarning("输入错误", "课程名称不能为空！", parent=self.update_course_win)
            return
        if not credits_str.isdigit() or int(credits_str) < 0:
            messagebox.showwarning("输入错误", "学分必须是非负整数！", parent=self.update_course_win)
            return
        credits = int(credits_str)
        try:
            if backend.update_course(course_id, name, teacher, credits, department):
                messagebox.showinfo("成功", "课程信息更新成功！", parent=self.update_course_win)
                self.update_course_win.destroy()
                self.load_courses() 
            else:
                messagebox.showerror("失败", "更新课程信息失败，可能是课程名称重复或数据库错误。", parent=self.update_course_win)
        except AttributeError:
             messagebox.showerror("后端函数错误", "backend.py 中缺少 update_course 函数。\n请确保该函数已正确定义。", parent=self.update_course_win)
        except Exception as e:
            messagebox.showerror("操作失败", f"更新课程时发生错误: {e}", parent=self.update_course_win)

    def delete_selected_course(self):
        selected_item = self.course_tree.focus()
        if not selected_item:
            messagebox.showwarning("操作无效", "请先在列表中选择一个课程进行删除。")
            return
        course_data = self.course_tree.item(selected_item, "values")
        course_id, course_name = course_data[0], course_data[1]
        if messagebox.askyesno("确认删除", f"您确定要删除课程 '{course_name}' (ID: {course_id}) 吗？\n此操作将同时删除与此课程相关的所有选课记录。"):
            try:
                if backend.delete_course(course_id):
                    messagebox.showinfo("成功", f"课程 '{course_name}' 删除成功！")
                    self.load_courses() 
                else:
                    messagebox.showerror("失败", f"删除课程 '{course_name}' 失败。")
            except AttributeError as ae:
                messagebox.showerror("后端函数错误", f"调用 backend.delete_course 时出错: {ae}\n请确保该函数已正确定义。")
            except Exception as e:
                 messagebox.showerror("操作失败", f"删除课程时发生错误: {e}")

    #-------------------------------------------------------------------
    # 选课管理相关 Widgets 和方法
    #-------------------------------------------------------------------
    def create_selection_widgets(self):
        top_frame = ttk.Frame(self.selection_tab, padding="10")
        top_frame.pack(fill=tk.X, pady=(0,10))
        student_sel_frame = ttk.Frame(top_frame)
        student_sel_frame.pack(side=tk.LEFT, padx=(0, 20), fill=tk.X, expand=True)
        ttk.Label(student_sel_frame, text="选择学生:").pack(side=tk.LEFT, padx=(0,5))
        self.sel_student_combo_var = tk.StringVar()
        self.sel_student_combo = ttk.Combobox(student_sel_frame, textvariable=self.sel_student_combo_var, state="readonly", width=25)
        self.sel_student_combo.pack(side=tk.LEFT, padx=(0,10))
        load_selected_courses_button = ttk.Button(student_sel_frame, text="查询该学生已选课程", command=self.load_student_selections_for_selected_student)
        load_selected_courses_button.pack(side=tk.LEFT)
        course_sel_frame = ttk.Frame(top_frame)
        course_sel_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(course_sel_frame, text="选择课程进行选课:").pack(side=tk.LEFT, padx=(0,5))
        self.sel_available_course_combo_var = tk.StringVar()
        self.sel_available_course_combo = ttk.Combobox(course_sel_frame, textvariable=self.sel_available_course_combo_var, state="readonly", width=30)
        self.sel_available_course_combo.pack(side=tk.LEFT, padx=(0,10))
        select_this_course_button = ttk.Button(course_sel_frame, text="选修此课程", command=self.process_student_select_course)
        select_this_course_button.pack(side=tk.LEFT)

        selected_courses_frame = ttk.LabelFrame(self.selection_tab, text="学生已选课程列表", padding="10")
        selected_courses_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.student_selections_tree = ttk.Treeview(selected_courses_frame, columns=("course_id", "course_name", "teacher", "credits", "grade", "selection_date"), show="headings")
        self.student_selections_tree.heading("course_id", text="课程ID")
        self.student_selections_tree.heading("course_name", text="课程名称")
        self.student_selections_tree.heading("teacher", text="教师")
        self.student_selections_tree.heading("credits", text="学分")
        self.student_selections_tree.heading("grade", text="成绩")
        self.student_selections_tree.heading("selection_date", text="选课日期")
        self.student_selections_tree.column("course_id", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.student_selections_tree.column("course_name", width=200, stretch=tk.YES)
        self.student_selections_tree.column("teacher", width=100, stretch=tk.NO)
        self.student_selections_tree.column("credits", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.student_selections_tree.column("grade", width=80, anchor=tk.CENTER, stretch=tk.NO)
        self.student_selections_tree.column("selection_date", width=150, stretch=tk.NO)
        self.student_selections_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sel_scrollbar = ttk.Scrollbar(selected_courses_frame, orient=tk.VERTICAL, command=self.student_selections_tree.yview)
        self.student_selections_tree.configure(yscroll=sel_scrollbar.set)
        sel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        selected_courses_action_frame = ttk.Frame(self.selection_tab, padding="5")
        selected_courses_action_frame.pack(fill=tk.X)
        drop_course_button = ttk.Button(selected_courses_action_frame, text="从已选列表退课", command=self.process_student_drop_course)
        drop_course_button.pack(side=tk.LEFT, padx=5)
        grade_course_button = ttk.Button(selected_courses_action_frame, text="录入/修改成绩", command=self.open_grade_entry_window)
        grade_course_button.pack(side=tk.LEFT, padx=5)

    def populate_selection_student_combobox(self):
        try:
            students = backend.get_all_students()
            if students:
                self.student_combo_map = {f"{s['student_id']} - {s['student_name']}": s['student_id'] for s in students}
                self.sel_student_combo['values'] = list(self.student_combo_map.keys())
                self.sel_student_combo.set('') 
            else:
                self.sel_student_combo['values'] = []
                self.sel_student_combo.set('')
        except Exception as e:
            messagebox.showerror("错误", f"加载学生列表到下拉框失败: {e}")
            self.sel_student_combo['values'] = []
            self.sel_student_combo.set('')
            
    def populate_selection_course_combobox(self):
        try:
            courses = backend.get_all_courses()
            if courses:
                self.course_combo_map = {f"{c['course_id']} - {c['course_name']}": c['course_id'] for c in courses}
                self.sel_available_course_combo['values'] = list(self.course_combo_map.keys())
                self.sel_available_course_combo.set('') 
            else:
                self.sel_available_course_combo['values'] = []
                self.sel_available_course_combo.set('')
        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表到下拉框失败: {e}")
            self.sel_available_course_combo['values'] = []
            self.sel_available_course_combo.set('')

    def get_selected_student_id_from_combo(self):
        display_val = self.sel_student_combo_var.get()
        return self.student_combo_map.get(display_val)

    def get_selected_course_id_from_combo(self):
        display_val = self.sel_available_course_combo_var.get()
        return self.course_combo_map.get(display_val)

    def load_student_selections_for_selected_student(self):
        for item in self.student_selections_tree.get_children():
            self.student_selections_tree.delete(item)
        student_id = self.get_selected_student_id_from_combo()
        if not student_id:
            messagebox.showwarning("提示", "请先选择一个学生。")
            return
        try:
            selected_courses = backend.get_student_selected_courses(student_id)
            if selected_courses:
                for sel_course in selected_courses:
                    grade_display = sel_course.get('grade', '') if sel_course.get('grade') is not None else "未录入"
                    self.student_selections_tree.insert("", tk.END, values=(
                        sel_course.get('course_id', ''),
                        sel_course.get('course_name', ''),
                        sel_course.get('teacher_name', ''),
                        sel_course.get('credits', ''),
                        grade_display,
                        sel_course.get('selection_date', '')
                    ))
        except AttributeError as ae:
            messagebox.showerror("后端函数错误", f"调用 backend.get_student_selected_courses 时出错: {ae}\n请确保该函数已正确定义。")
        except Exception as e:
            messagebox.showerror("加载已选课程失败", f"发生错误: {e}")

    def process_student_select_course(self):
        student_id = self.get_selected_student_id_from_combo()
        course_id = self.get_selected_course_id_from_combo()
        if not student_id:
            messagebox.showwarning("操作无效", "请先选择一个学生。", parent=self.selection_tab)
            return
        if not course_id:
            messagebox.showwarning("操作无效", "请选择要选修的课程。", parent=self.selection_tab)
            return
        try:
            if backend.select_course(student_id, course_id):
                messagebox.showinfo("成功", "选课成功！", parent=self.selection_tab)
                self.load_student_selections_for_selected_student() 
                self.load_courses() 
            else:
                messagebox.showerror("失败", "选课失败。\n可能原因：学生已选此课程，或数据库操作错误。", parent=self.selection_tab)
        except AttributeError as ae:
            messagebox.showerror("后端函数错误", f"调用 backend.select_course 时出错: {ae}\n请确保该函数已正确定义。", parent=self.selection_tab)
        except Exception as e:
            messagebox.showerror("操作失败", f"选课时发生错误: {e}", parent=self.selection_tab)

    def process_student_drop_course(self):
        selected_item_in_tree = self.student_selections_tree.focus()
        if not selected_item_in_tree:
            messagebox.showwarning("操作无效", "请先在下方“学生已选课程列表”中选择要退选的课程。", parent=self.selection_tab)
            return
        student_id = self.get_selected_student_id_from_combo() 
        if not student_id: 
            messagebox.showwarning("操作无效", "请先在上方选择一个学生。", parent=self.selection_tab)
            return
        selected_course_data = self.student_selections_tree.item(selected_item_in_tree, "values")
        course_id_to_drop = selected_course_data[0]
        course_name_to_drop = selected_course_data[1]
        student_display_name = self.sel_student_combo_var.get()
        if messagebox.askyesno("确认退课", f"您确定要为学生 '{student_display_name}' 退选课程 '{course_name_to_drop}' (ID: {course_id_to_drop}) 吗？", parent=self.selection_tab):
            try:
                if backend.drop_course(student_id, course_id_to_drop):
                    messagebox.showinfo("成功", "退课成功！", parent=self.selection_tab)
                    self.load_student_selections_for_selected_student() 
                    self.load_courses() 
                else:
                    messagebox.showerror("失败", "退课失败。", parent=self.selection_tab)
            except AttributeError as ae:
                messagebox.showerror("后端函数错误", f"调用 backend.drop_course 时出错: {ae}\n请确保该函数已正确定义。", parent=self.selection_tab)
            except Exception as e:
                messagebox.showerror("操作失败", f"退课时发生错误: {e}", parent=self.selection_tab)

    def open_grade_entry_window(self):
        selected_item_in_tree = self.student_selections_tree.focus()
        if not selected_item_in_tree:
            messagebox.showwarning("操作无效", "请先在下方“学生已选课程列表”中选择要录入成绩的课程。", parent=self.selection_tab)
            return
        student_id = self.get_selected_student_id_from_combo()
        if not student_id:
            messagebox.showwarning("操作无效", "请先在上方选择一个学生。", parent=self.selection_tab)
            return
        selected_course_data = self.student_selections_tree.item(selected_item_in_tree, "values")
        course_id = selected_course_data[0]
        course_name = selected_course_data[1]
        current_grade = selected_course_data[4] 
        if current_grade == "未录入":
            current_grade = ""
        self.grade_entry_win = tk.Toplevel(self.root)
        self.grade_entry_win.title(f"为课程 '{course_name}' 录入成绩")
        self.grade_entry_win.geometry("300x150")
        self.grade_entry_win.transient(self.root)
        self.grade_entry_win.grab_set()
        form_frame = ttk.Frame(self.grade_entry_win, padding="15")
        form_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(form_frame, text="学生:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text=self.sel_student_combo_var.get()).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text="课程:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text=course_name).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(form_frame, text="成绩:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.grade_entry_field = ttk.Entry(form_frame, width=15)
        self.grade_entry_field.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.grade_entry_field.insert(0, str(current_grade))
        self.grade_student_id = student_id
        self.grade_course_id = course_id
        save_grade_button = ttk.Button(form_frame, text="保存成绩", command=self.save_course_grade)
        save_grade_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.grade_entry_field.focus_set()
        self.grade_entry_field.selection_range(0, tk.END)

    def save_course_grade(self):
        grade_str = self.grade_entry_field.get().strip()
        student_id = self.grade_student_id
        course_id = self.grade_course_id
        if not grade_str: 
            grade = None
        else:
            try:
                grade = float(grade_str)
                if not (0 <= grade <= 1000): 
                     messagebox.showwarning("输入错误", "成绩必须是有效的数字 (例如 0-100)。", parent=self.grade_entry_win)
                     return
            except ValueError:
                messagebox.showwarning("输入错误", "成绩必须是有效的数字。", parent=self.grade_entry_win)
                return
        try:
            if backend.record_grade(student_id, course_id, grade):
                messagebox.showinfo("成功", "成绩保存成功！", parent=self.grade_entry_win)
                self.grade_entry_win.destroy()
                self.load_student_selections_for_selected_student() 
                self.load_grade_audit_logs() # 成绩变更后刷新审计日志
            else:
                messagebox.showerror("失败", "保存成绩失败。", parent=self.grade_entry_win)
        except AttributeError as ae:
            messagebox.showerror("后端函数错误", f"调用 backend.record_grade 时出错: {ae}\n请确保该函数已正确定义。", parent=self.grade_entry_win)
        except Exception as e:
            messagebox.showerror("操作失败", f"保存成绩时发生错误: {e}", parent=self.grade_entry_win)

    #-------------------------------------------------------------------
    # 成绩审计日志相关 Widgets 和方法
    #-------------------------------------------------------------------
    def create_audit_log_widgets(self):
        # --- 操作按钮区域 (审计日志) ---
        audit_action_frame = ttk.Frame(self.audit_log_tab, padding="10")
        audit_action_frame.pack(fill=tk.X, pady=(0,10))

        self.refresh_audit_button = ttk.Button(audit_action_frame, text="刷新日志", command=self.load_grade_audit_logs)
        self.refresh_audit_button.pack(side=tk.LEFT, padx=5)

        # --- 审计日志列表显示区域 ---
        audit_list_frame = ttk.LabelFrame(self.audit_log_tab, text="成绩变更记录", padding="10")
        audit_list_frame.pack(fill=tk.BOTH, expand=True)

        self.audit_log_tree = ttk.Treeview(audit_list_frame, columns=("log_id", "sel_id", "stud_name", "cour_name", "old_g", "new_g", "user", "time"), show="headings")
        self.audit_log_tree.heading("log_id", text="日志ID")
        self.audit_log_tree.heading("sel_id", text="选课ID")
        self.audit_log_tree.heading("stud_name", text="学生姓名")
        self.audit_log_tree.heading("cour_name", text="课程名称")
        self.audit_log_tree.heading("old_g", text="原成绩")
        self.audit_log_tree.heading("new_g", text="新成绩")
        self.audit_log_tree.heading("user", text="操作者") # 数据库触发器默认为 DB_TRIGGER
        self.audit_log_tree.heading("time", text="变更时间")

        self.audit_log_tree.column("log_id", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.audit_log_tree.column("sel_id", width=60, anchor=tk.CENTER, stretch=tk.NO)
        self.audit_log_tree.column("stud_name", width=120, stretch=tk.YES)
        self.audit_log_tree.column("cour_name", width=180, stretch=tk.YES)
        self.audit_log_tree.column("old_g", width=70, anchor=tk.CENTER, stretch=tk.NO)
        self.audit_log_tree.column("new_g", width=70, anchor=tk.CENTER, stretch=tk.NO)
        self.audit_log_tree.column("user", width=100, stretch=tk.NO)
        self.audit_log_tree.column("time", width=150, stretch=tk.NO)

        self.audit_log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        audit_scrollbar = ttk.Scrollbar(audit_list_frame, orient=tk.VERTICAL, command=self.audit_log_tree.yview)
        self.audit_log_tree.configure(yscroll=audit_scrollbar.set)
        audit_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_grade_audit_logs(self):
        """从数据库加载成绩审计日志并显示"""
        for item in self.audit_log_tree.get_children():
            self.audit_log_tree.delete(item)
        try:
            # 假设 backend.py 中有 get_grade_audit_logs 函数
            # 该函数应返回包含 student_name 和 course_name (通过JOIN获取) 的日志记录
            audit_data = backend.get_grade_audit_logs() 
            if audit_data:
                for log in audit_data:
                    old_grade_display = log.get('old_grade', '') if log.get('old_grade') is not None else "N/A"
                    new_grade_display = log.get('new_grade', '') if log.get('new_grade') is not None else "N/A"
                    self.audit_log_tree.insert("", tk.END, values=(
                        log.get('log_id', ''),
                        log.get('selection_id', ''), # 假设后端返回此字段
                        log.get('student_name', f"学生ID:{log.get('student_id','未知')}"), # 优先显示姓名
                        log.get('course_name', f"课程ID:{log.get('course_id','未知')}"), # 优先显示课程名
                        old_grade_display,
                        new_grade_display,
                        log.get('changed_by', 'DB_TRIGGER'),
                        log.get('change_timestamp', '')
                    ))
        except AttributeError as ae:
             messagebox.showerror("后端函数错误", f"调用 backend.py 中的函数时出错: {ae}\n请确保 get_grade_audit_logs 函数已正确定义。")
        except Exception as e:
            messagebox.showerror("加载审计日志失败", f"发生错误: {e}\n请确保数据库连接正常且相关函数无误。")


if __name__ == "__main__":
    try:
        conn_test, _ = backend.get_db_connection()
        if not conn_test:
            root_temp = tk.Tk()
            root_temp.withdraw() 
            messagebox.showerror("数据库连接失败", "无法连接到数据库，请检查 backend.py 中的 DB_CONFIG。GUI 将无法启动。")
            root_temp.destroy()
            exit()
        else:
            conn_test.close()
            
        root = tk.Tk()
        style = ttk.Style(root)
        try:
            if "clam" in style.theme_names(): style.theme_use("clam")
            elif "vista" in style.theme_names(): style.theme_use("vista")
            elif "aqua" in style.theme_names(): style.theme_use("aqua")
        except tk.TclError:
            print("未能成功应用ttk主题，将使用默认主题。")

        app = StudentCourseApp(root)
        root.mainloop()

    except AttributeError as ae:
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror("后端函数缺失", f"backend.py 中缺少必要的函数 (如 get_db_connection): {ae}")
        root_temp.destroy()
    except Exception as e:
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror("启动错误", f"应用程序启动时发生未知错误: {e}")
        root_temp.destroy()
