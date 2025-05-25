import mysql.connector
from datetime import datetime

# --- 数据库连接配置 ---
DB_CONFIG = {
    'host': 'localhost',      # 你的 MySQL 服务器地址
    'user': 'root',  # 你的 MySQL 用户名
    'password': 'mysql',# 你的 MySQL 密码
    'database': 'student_course_system' # 你创建的数据库名
}

def get_db_connection():
    """获取数据库连接和游标"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True) # dictionary=True 使查询结果为字典形式
        return conn, cursor
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None, None

# --- 学生管理 ---
def add_student(name, gender, enrollment_year, email):
    """添加新学生"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        sql = "INSERT INTO students (student_name, student_gender, enrollment_year, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, gender, enrollment_year, email))
        conn.commit()
        print(f"学生 '{name}' 添加成功！ID: {cursor.lastrowid}")
        return True
    except mysql.connector.Error as err:
        print(f"添加学生失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_student_by_id(student_id):
    """根据ID查询学生"""
    conn, cursor = get_db_connection()
    if not conn:
        return None
    try:
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        return student
    except mysql.connector.Error as err:
        print(f"查询学生失败: {err}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_all_students():
    """查询所有学生"""
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        return students
    except mysql.connector.Error as err:
        print(f"查询所有学生失败: {err}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def update_student_email(student_id, new_email):
    """更新学生邮箱"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        sql = "UPDATE students SET email = %s WHERE student_id = %s"
        cursor.execute(sql, (new_email, student_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"学生ID {student_id} 的邮箱更新成功！")
            return True
        else:
            print(f"未找到学生ID {student_id} 或邮箱未改变。")
            return False
    except mysql.connector.Error as err:
        print(f"更新学生邮箱失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def delete_student(student_id):
    """删除学生"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        # 注意：由于设置了外键的 ON DELETE CASCADE，相关的选课记录也会被删除
        sql = "DELETE FROM students WHERE student_id = %s"
        cursor.execute(sql, (student_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"学生ID {student_id} 删除成功！")
            return True
        else:
            print(f"未找到学生ID {student_id}。")
            return False
    except mysql.connector.Error as err:
        print(f"删除学生失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

# --- 课程管理 ---
def add_course(course_name, teacher_name, credits, department):
    """添加新课程"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        sql = "INSERT INTO courses (course_name, teacher_name, credits, department) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (course_name, teacher_name, credits, department))
        conn.commit()
        print(f"课程 '{course_name}' 添加成功！ID: {cursor.lastrowid}")
        return True
    except mysql.connector.Error as err:
        print(f"添加课程失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_course_by_id(course_id):
    """根据ID查询课程"""
    conn, cursor = get_db_connection()
    if not conn:
        return None
    try:
        cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
        course = cursor.fetchone()
        return course
    except mysql.connector.Error as err:
        print(f"查询课程失败: {err}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_all_courses():
    """查询所有课程"""
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        return courses
    except mysql.connector.Error as err:
        print(f"查询所有课程失败: {err}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def delete_course(course_id):
    """删除课程"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        # 注意：由于设置了外键的 ON DELETE CASCADE，相关的选课记录也会被删除
        sql = "DELETE FROM courses WHERE course_id = %s"
        cursor.execute(sql, (course_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"课程ID {course_id} 删除成功！")
            return True
        else:
            print(f"未找到课程ID {course_id}。")
            return False
    except mysql.connector.Error as err:
        print(f"删除课程失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

# --- 选课管理 ---
def select_course(student_id, course_id):
    """学生选课"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        # 检查学生和课程是否存在
        student = get_student_by_id(student_id)
        course = get_course_by_id(course_id)
        if not student:
            print(f"错误：学生ID {student_id} 不存在。")
            return False
        if not course:
            print(f"错误：课程ID {course_id} 不存在。")
            return False

        sql = "INSERT INTO selections (student_id, course_id, selection_date) VALUES (%s, %s, %s)"
        current_time = datetime.now()
        cursor.execute(sql, (student_id, course_id, current_time))
        conn.commit()
        print(f"学生ID {student_id} 选修课程ID {course_id} 成功！")
        return True
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry
             print(f"选课失败: 学生ID {student_id} 已选修课程ID {course_id}。")
        else:
            print(f"选课失败: {err}")
        return False
    finally:
        if conn: # conn 可能因为 get_student_by_id 中的错误而为 None
            cursor.close()
            conn.close()


def drop_course(student_id, course_id):
    """学生退课"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        sql = "DELETE FROM selections WHERE student_id = %s AND course_id = %s"
        cursor.execute(sql, (student_id, course_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"学生ID {student_id} 退选课程ID {course_id} 成功！")
            return True
        else:
            print(f"未找到学生ID {student_id} 对课程ID {course_id} 的选课记录。")
            return False
    except mysql.connector.Error as err:
        print(f"退课失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_student_selected_courses(student_id):
    """查询某学生已选的所有课程"""
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        # 使用 JOIN 查询课程名等详细信息
        sql = """
            SELECT c.course_id, c.course_name, c.teacher_name, c.credits, s.selection_date, s.grade
            FROM courses c
            JOIN selections s ON c.course_id = s.course_id
            WHERE s.student_id = %s
        """
        cursor.execute(sql, (student_id,))
        selected_courses = cursor.fetchall()
        return selected_courses
    except mysql.connector.Error as err:
        print(f"查询学生已选课程失败: {err}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_course_enrolled_students(course_id):
    """查询某课程的所有选课学生"""
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        # 使用 JOIN 查询学生名等详细信息
        sql = """
            SELECT st.student_id, st.student_name, st.email, s.selection_date, s.grade
            FROM students st
            JOIN selections s ON st.student_id = s.student_id
            WHERE s.course_id = %s
        """
        cursor.execute(sql, (course_id,))
        enrolled_students = cursor.fetchall()
        return enrolled_students
    except mysql.connector.Error as err:
        print(f"查询课程选课学生失败: {err}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def record_grade(student_id, course_id, grade):
    """为学生的某门已选课程记录成绩"""
    conn, cursor = get_db_connection()
    if not conn:
        return False
    try:
        sql = "UPDATE selections SET grade = %s WHERE student_id = %s AND course_id = %s"
        cursor.execute(sql, (grade, student_id, course_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"学生ID {student_id} 的课程ID {course_id} 成绩录入为 {grade} 成功！")
            return True
        else:
            print(f"未找到学生ID {student_id} 对课程ID {course_id} 的选课记录，或成绩未改变。")
            return False
    except mysql.connector.Error as err:
        print(f"录入成绩失败: {err}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def print_courses(courses):
    if not courses:
        print("没有课程信息。")
        return
    print("\n--- 所有课程 ---")
    # 添加 enrollment_count 到表头和内容
    print(f"{'ID':<5} {'课程名':<20} {'教师':<10} {'学分':<5} {'院系':<15} {'选课人数':<10}")
    print("-" * 70) # 分隔线
    for course in courses:
        print(f"{course['course_id']:<5} {course['course_name']:<20} {course.get('teacher_name', 'N/A'):<10} "
              f"{course.get('credits', 'N/A'):<5} {course.get('department', 'N/A'):<15} "
              f"{course.get('enrollment_count', 0):<10}") # 使用 .get() 增加健壮性
    print("----------------------------------------------------------------------")            


# (添加到之前的 Python 代码中)

def get_grade_audit_logs(limit=20):
    """查询最近的成绩变更日志"""
    conn, cursor = get_db_connection()
    if not conn:
        return []
    try:
        # 查询时可以 JOIN students 和 courses 表来获取更详细的姓名和课程名
        sql = """
            SELECT gal.log_id, gal.selection_id,
                   s.student_name, c.course_name,
                   gal.old_grade, gal.new_grade, gal.change_timestamp
            FROM grade_audit_log gal
            LEFT JOIN students s ON gal.student_id = s.student_id
            LEFT JOIN courses c ON gal.course_id = c.course_id
            ORDER BY gal.change_timestamp DESC
            LIMIT %s
        """
        cursor.execute(sql, (limit,))
        logs = cursor.fetchall()
        return logs
    except mysql.connector.Error as err:
        print(f"查询成绩审计日志失败: {err}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def print_grade_audit_logs(logs):
    if not logs:
        print("没有成绩变更日志。")
        return
    print("\n--- 成绩变更审计日志 ---")
    print(f"{'LogID':<7} {'Sel.ID':<7} {'学生名':<15} {'课程名':<20} {'旧成绩':<7} {'新成绩':<7} {'变更时间':<20}")
    print("-" * 90)
    for log in logs:
        s_name = log.get('student_name') if log.get('student_name') else f"SID:{log['student_id']}" # 如果学生被删除
        c_name = log.get('course_name') if log.get('course_name') else f"CID:{log['course_id']}" # 如果课程被删除
        print(f"{log['log_id']:<7} {log.get('selection_id', 'N/A'):<7} {s_name:<15} "
              f"{c_name:<20} {str(log['old_grade']) if log['old_grade'] is not None else 'NULL':<7} "
              f"{str(log['new_grade']) if log['new_grade'] is not None else 'NULL':<7} "
              f"{log['change_timestamp']}")
    print("------------------------------------------------------------------------------------------")

# 在 main_menu 或一个管理员菜单中添加调用选项：
# ...
# elif choice == '4': # 假设 '4' 是查看审计日志
#     logs = get_grade_audit_logs()
#     print_grade_audit_logs(logs)
# ...