-- 创建数据库 (如果尚未创建)
CREATE DATABASE IF NOT EXISTS student_course_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_course_system;

-- 1. 学生表 (Students)
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_gender ENUM('男', '女', '其他') DEFAULT '其他',
    enrollment_year YEAR,
    email VARCHAR(100) UNIQUE
);

-- 2. 课程表 (Courses)
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL UNIQUE,
    teacher_name VARCHAR(100),
    credits INT DEFAULT 0,
    department VARCHAR(100)
);

-- 3. 选课记录表 (Selections)
CREATE TABLE IF NOT EXISTS selections (
    selection_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    selection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade DECIMAL(5, 2), -- 可以存储百分制成绩，例如 88.50
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY (student_id, course_id) --确保一个学生对一门课只能选一次
);

-- 插入一些示例数据 (可选)
INSERT INTO students (student_name, student_gender, enrollment_year, email) VALUES
('张三', '男', 2023, 'zhangsan@example.com'),
('李四', '女', 2022, 'lisi@example.com'),
('王五', '男', 2023, 'wangwu@example.com');

INSERT INTO courses (course_name, teacher_name, credits, department) VALUES
('数据库原理', '赵老师', 3, '计算机系'),
('操作系统', '钱老师', 4, '计算机系'),
('高等数学', '孙老师', 5, '数学系');