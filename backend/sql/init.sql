-- 1. Таблица пользователей (User)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student', -- 'teacher', 'student', 'admin'
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Индекс для быстрого логина
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Таблица предметов (Subject)
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    author_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Таблица тем (Topic)
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    order_index INT DEFAULT 0
);

-- 4. Таблица учебных групп (StudyGroup)
CREATE TABLE IF NOT EXISTS study_groups (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    invite_code VARCHAR(32) UNIQUE NOT NULL,
    teacher_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- 5. Связующая таблица: Студенты в группах (GroupMember)
CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    group_id INT NOT NULL REFERENCES study_groups(id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_group_student UNIQUE (group_id, student_id)
);

-- 6. Таблица заданий / банка задач (Task)
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    parent_task_id INT REFERENCES tasks(id) ON DELETE SET NULL, -- Для AI-вариаций
    title VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- 'single_choice', 'numeric', 'code', 'open_answer'
    difficulty VARCHAR(20) DEFAULT 'medium',
    points INT DEFAULT 1,
    content JSONB NOT NULL,
    validation_schema JSONB NOT NULL,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_metadata JSONB DEFAULT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- 7. Таблица тестов / проверочных работ (Test)
CREATE TABLE IF NOT EXISTS tests (
    id SERIAL PRIMARY KEY,
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    group_id INT REFERENCES study_groups(id) ON DELETE SET NULL,
    author_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    time_limit_minutes INT DEFAULT NULL,
    deadline TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- 8. Связующая таблица: Задачи в тесте (TestTask)
CREATE TABLE IF NOT EXISTS test_tasks (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    order_index INT DEFAULT 0,
    CONSTRAINT uq_test_task UNIQUE (test_id, task_id)
);

-- 9. Таблица сдач тестов (Submission)
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'in_progress', -- 'in_progress', 'submitted', 'graded'
    total_score NUMERIC(5, 2) DEFAULT 0.0,
    started_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL
);

-- 10. Таблица ответов студента на конкретные задачи (StudentAnswer)
CREATE TABLE IF NOT EXISTS student_answers (
    id SERIAL PRIMARY KEY,
    submission_id INT NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    student_response JSONB NOT NULL,
    earned_points NUMERIC(5, 2) DEFAULT 0.0,
    teacher_comment TEXT DEFAULT NULL
);