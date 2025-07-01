# setup_larvae_database_alt.py
import psycopg2

DATABASE_URL = "postgresql://datalog_db_user:qjRhbSTVENtpfIZbMGC4GhuUa01EtZ48@dpg-d1haovvdiees738l5gb0-a.virginia-postgres.render.com/datalog_db"

sql = """
-- Drop the old table if it exists
DROP TABLE IF EXISTS larvae_logs CASCADE;

-- Create with new structure using 'username' instead of 'user'
CREATE TABLE larvae_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    username VARCHAR(100) NOT NULL,  -- Changed from 'user' to 'username'
    days_of_age INTEGER NOT NULL,
    larva_weight INTEGER NOT NULL,
    larva_pct INTEGER NOT NULL,
    lb_larvae INTEGER NOT NULL,
    lb_feed DECIMAL(10,2) NOT NULL,
    lb_water DECIMAL(10,2) NOT NULL,
    screen_refeed BOOLEAN DEFAULT FALSE,
    row_number VARCHAR(50),
    notes TEXT,
    larvae_count INTEGER,
    feed_per_larvae DECIMAL(10,1),
    water_feed_ratio DECIMAL(10,1)
);

-- Create indexes
CREATE INDEX idx_larvae_logs_timestamp ON larvae_logs(timestamp DESC);
CREATE INDEX idx_larvae_logs_username ON larvae_logs(username);
"""

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("✅ Table created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()