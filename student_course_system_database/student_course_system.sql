-- 1. 创建数据库并切换
CREATE DATABASE IF NOT EXISTS student_course_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_course_system;

-- 2. 学生表
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_gender ENUM('男', '女', '其他') DEFAULT '其他',
    enrollment_year YEAR,
    email VARCHAR(100) UNIQUE
);

-- 3. 课程表
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL UNIQUE,
    teacher_name VARCHAR(100),
    credits INT DEFAULT 0,
    department VARCHAR(100),
    enrollment_count INT DEFAULT 0 COMMENT '当前选课人数'
);

-- 4. 选课记录表
CREATE TABLE IF NOT EXISTS selections (
    selection_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    selection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade DECIMAL(5, 2),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY (student_id, course_id)
);


-- 5. 初始化示例数据
INSERT INTO students (student_name, student_gender, enrollment_year, email) VALUES
('张三', '男', 2023, 'zhangsan@example.com'),
('李四', '女', 2022, 'lisi@example.com'),
('王五', '男', 2023, 'wangwu@example.com');

INSERT INTO courses (course_name, teacher_name, credits, department) VALUES
('数据库原理', '赵老师', 3, '计算机系'),
('操作系统', '钱老师', 4, '计算机系'),
('高等数学', '孙老师', 5, '数学系');

-- 6. 若已存在选课数据，初始化选课人数
UPDATE courses c
SET c.enrollment_count = (
    SELECT COUNT(*) FROM selections s WHERE s.course_id = c.course_id
);

-- 7. 成绩变更审计日志表
CREATE TABLE IF NOT EXISTS grade_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    selection_id INT,
    student_id INT,
    course_id INT,
    old_grade DECIMAL(5,2),
    new_grade DECIMAL(5,2),
    changed_by VARCHAR(100) DEFAULT 'DB_TRIGGER',
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);

-- 8. 触发器：选课插入后，课程人数+1
DELIMITER $$
CREATE TRIGGER trg_after_selection_insert
AFTER INSERT ON selections
FOR EACH ROW
BEGIN
    UPDATE courses
    SET enrollment_count = enrollment_count + 1
    WHERE course_id = NEW.course_id;
END $$
DELIMITER ;

-- 9. 触发器：选课删除后，课程人数-1（不为负数）
DELIMITER $$
CREATE TRIGGER trg_after_selection_delete
AFTER DELETE ON selections
FOR EACH ROW
BEGIN
    UPDATE courses
    SET enrollment_count = IF(enrollment_count > 0, enrollment_count - 1, 0)
    WHERE course_id = OLD.course_id;
END $$
DELIMITER ;

-- 10. 触发器：成绩变更写入审计日志
DELIMITER $$
CREATE TRIGGER trg_after_selection_grade_update
AFTER UPDATE ON selections
FOR EACH ROW
BEGIN
    IF ( (OLD.grade <> NEW.grade) OR (OLD.grade IS NULL AND NEW.grade IS NOT NULL) OR (OLD.grade IS NOT NULL AND NEW.grade IS NULL) ) THEN
        INSERT INTO grade_audit_log (selection_id, student_id, course_id, old_grade, new_grade, change_timestamp)
        VALUES (OLD.selection_id, OLD.student_id, OLD.course_id, OLD.grade, NEW.grade, NOW());
    END IF;
END $$student_id
DELIMITER ;
