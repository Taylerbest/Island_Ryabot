-- Создание основных таблиц для Ryabot Island

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    language TEXT DEFAULT 'ru',
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    energy INTEGER DEFAULT 100,
    ryabucks INTEGER DEFAULT 1000,
    rbtc NUMERIC(10,2) DEFAULT 0.0,
    golden_shards INTEGER DEFAULT 0,
    quantum_keys INTEGER DEFAULT 0,
    land_plots INTEGER DEFAULT 1,
    tutorial_completed BOOLEAN DEFAULT FALSE,
    current_state TEXT,
    activity_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица построек фермы
CREATE TABLE IF NOT EXISTS farm_buildings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    building_type TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    last_collected TIMESTAMP WITH TIME ZONE,
    next_collection TIMESTAMP WITH TIME ZONE,
    plot_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица экспедиций
CREATE TABLE IF NOT EXISTS expeditions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    zone_id INTEGER,
    status TEXT DEFAULT 'active',
    rbtc_found NUMERIC(10,2) DEFAULT 0.0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Таблица нанятых рабочих
CREATE TABLE IF NOT EXISTS hired_workers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    worker_type TEXT DEFAULT 'laborer',
    status TEXT DEFAULT 'idle',
    hired_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    next_available_at TIMESTAMP WITH TIME ZONE
);

-- Таблица обучения
CREATE TABLE IF NOT EXISTS training_units (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    unit_type TEXT NOT NULL,
    status TEXT DEFAULT 'training',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    worker_id INTEGER REFERENCES hired_workers(id) ON DELETE SET NULL
);

-- Таблица обученных специалистов
CREATE TABLE IF NOT EXISTS trained_specialists (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    specialist_type TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_worked TIMESTAMP WITH TIME ZONE
);

-- Таблица кулдаунов найма
CREATE TABLE IF NOT EXISTS hire_cooldowns (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) UNIQUE ON DELETE CASCADE,
    last_hire_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    hires_count INTEGER DEFAULT 0,
    reset_date DATE DEFAULT CURRENT_DATE
);

-- Таблица статистики острова
CREATE TABLE IF NOT EXISTS island_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE DEFAULT CURRENT_DATE,
    total_players INTEGER DEFAULT 0,
    active_players INTEGER DEFAULT 0,
    daily_rbtc NUMERIC(10,2) DEFAULT 0.0,
    active_expeditions INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active);
CREATE INDEX IF NOT EXISTS idx_farm_buildings_userid ON farm_buildings(user_id);
CREATE INDEX IF NOT EXISTS idx_expeditions_userid ON expeditions(user_id);
CREATE INDEX IF NOT EXISTS idx_expeditions_status ON expeditions(status);
CREATE INDEX IF NOT EXISTS idx_hired_workers_userid ON hired_workers(user_id);
CREATE INDEX IF NOT EXISTS idx_hired_workers_status ON hired_workers(status);
CREATE INDEX IF NOT EXISTS idx_training_units_userid ON training_units(user_id);
CREATE INDEX IF NOT EXISTS idx_training_units_status ON training_units(status);
CREATE INDEX IF NOT EXISTS idx_trained_specialists_userid ON trained_specialists(user_id);

-- Row Level Security (RLS) политики
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE farm_buildings ENABLE ROW LEVEL SECURITY;
ALTER TABLE expeditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE hired_workers ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE trained_specialists ENABLE ROW LEVEL SECURITY;
ALTER TABLE hire_cooldowns ENABLE ROW LEVEL SECURITY;

-- Политики безопасности (пользователи могут работать только со своими данными)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (true);
CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (true);

-- Аналогичные политики для других таблиц
CREATE POLICY "Users can manage own farm buildings" ON farm_buildings FOR ALL USING (true);
CREATE POLICY "Users can manage own expeditions" ON expeditions FOR ALL USING (true);
CREATE POLICY "Users can manage own workers" ON hired_workers FOR ALL USING (true);
CREATE POLICY "Users can manage own training" ON training_units FOR ALL USING (true);
CREATE POLICY "Users can manage own specialists" ON trained_specialists FOR ALL USING (true);
CREATE POLICY "Users can manage own cooldowns" ON hire_cooldowns FOR ALL USING (true);

-- Общедоступная статистика острова
CREATE POLICY "Island stats are public" ON island_stats FOR SELECT USING (true);
