# --- Over / Under 2.5 (3-Way Arbitrage) ---
query_over_under = """
WITH joined_data AS (
    SELECT 
        t1.Team1, t1.Team2,
        -- Novibet Odds
        t1.O_odd as O_novi, t1.U_odd as U_novi,
        -- Stoiximan Odds
        t2.O_odd as O_stoi, t2.U_odd as U_stoi,
        -- Efbet Odds
        t3.O_odds as O_ef, t3.U_odds as U_ef
    FROM table1 t1 -- Novibet
    INNER JOIN table2 t2 ON t1.Team1 = t2.Team1 -- Stoiximan
    INNER JOIN table3 t3 ON t1.Team1 = t3.Team1 -- Efbet
    WHERE 
        t1.O_odd IS NOT NULL AND t2.O_odd IS NOT NULL AND t3.O_odds IS NOT NULL
),
calc_max AS (
    SELECT 
        *,
        -- Find Best Odds across all 3
        GREATEST(O_novi, O_stoi, O_ef) as O_max,
        GREATEST(U_novi, U_stoi, U_ef) as U_max
    FROM joined_data
),
calc_arb AS (
    SELECT 
        *,
        -- Calculate Arbitrage %
        (1/O_max + 1/U_max) as arb
    FROM calc_max
)
SELECT * FROM calc_arb 
WHERE arb < 1.00
ORDER BY arb ASC;
"""

# --- GG / NG (2-Way Arbitrage) ---
query_gg_ng = """
WITH joined_data AS (
    SELECT 
        t1.Team1, t1.Team2,
        -- Novibet
        t1.GG_odd as GG_novi, t1.NG_odd as NG_novi,
        -- Stoiximan
        t2.GG_odd as GG_stoi, t2.NG_odd as NG_stoi
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.Team1 = t2.Team1
    WHERE t1.GG_odd IS NOT NULL AND t2.GG_odd IS NOT NULL
),
calc_max AS (
    SELECT 
        *,
        GREATEST(GG_novi, GG_stoi) as GG_max,
        GREATEST(NG_novi, NG_stoi) as NG_max
    FROM joined_data
),
calc_arb AS (
    SELECT 
        *,
        (1/GG_max + 1/NG_max) as arb
    FROM calc_max
)
SELECT * FROM calc_arb 
WHERE arb < 1.00
ORDER BY arb ASC;
"""

# --- 1 X 2 (3-Way Arbitrage) ---
query_1X2 = """
WITH joined_data AS (
    SELECT 
        t1.Team1, t1.Team2,
        -- Novibet
        t1.One_odd as '1_novi', t1.X_odd as 'X_novi', t1.Two_odd as '2_novi',
        -- Stoiximan
        t2.One_odd as '1_stoi', t2.X_odd as 'X_stoi', t2.Two_odd as '2_stoi',
        -- Efbet
        t3."1" as '1_ef', t3."X" as 'X_ef', t3."2" as '2_ef'
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.Team1 = t2.Team1
    INNER JOIN table3 t3 ON t1.Team1 = t3.Team1
    WHERE 
        t1.One_odd IS NOT NULL AND t2.One_odd IS NOT NULL AND t3."1" IS NOT NULL
),
calc_max AS (
    SELECT 
        *,
        GREATEST("1_novi", "1_stoi", "1_ef") as "1_max",
        GREATEST("X_novi", "X_stoi", "X_ef") as "X_max",
        GREATEST("2_novi", "2_stoi", "2_ef") as "2_max"
    FROM joined_data
),
calc_arb AS (
    SELECT 
        *,
        (1/"1_max" + 1/"X_max" + 1/"2_max") as arb
    FROM calc_max
)
SELECT * FROM calc_arb 
WHERE arb < 1.00
ORDER BY arb ASC;
"""
