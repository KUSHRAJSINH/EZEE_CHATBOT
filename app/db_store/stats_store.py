import aiosqlite
import time

DB_PATH = "stats.db"


async def init_db() -> None:
    """
    Create the stats table if it does not already exist.
    Called once at application startup.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_stats (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id          TEXT    NOT NULL,
                latency_ms      REAL    NOT NULL,
                input_tokens    INTEGER NOT NULL,
                output_tokens   INTEGER NOT NULL,
                is_unanswered   INTEGER NOT NULL DEFAULT 0,
                timestamp       REAL    NOT NULL
            )
        """)
        await db.commit()


async def record_stat(
    bot_id: str,
    latency_ms: float,
    input_tokens: int,
    output_tokens: int,
    is_unanswered: bool,
) -> None:
    """
    Persist one chat turn's stats to SQLite.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO chat_stats
                (bot_id, latency_ms, input_tokens, output_tokens, is_unanswered, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                bot_id,
                latency_ms,
                input_tokens,
                output_tokens,
                1 if is_unanswered else 0,
                time.time(),
            ),
        )
        await db.commit()


async def get_stats(bot_id: str) -> dict:
    """
    Aggregate stats for a bot and return the StatsResponse-compatible dict.

    Token cost model (Groq llama-3.1-8b — free tier, but we estimate for transparency):
      Input:  $0.05 / 1M tokens
      Output: $0.08 / 1M tokens
    """
    INPUT_PRICE_PER_TOKEN  = 0.05 / 1_000_000
    OUTPUT_PRICE_PER_TOKEN = 0.08 / 1_000_000

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT
                COUNT(*)                        AS total_messages,
                COALESCE(AVG(latency_ms), 0)    AS avg_latency_ms,
                COALESCE(SUM(input_tokens), 0)  AS total_input_tokens,
                COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
                COALESCE(SUM(is_unanswered), 0) AS unanswered_questions
            FROM chat_stats
            WHERE bot_id = ?
            """,
            (bot_id,),
        ) as cursor:
            row = await cursor.fetchone()

    total_messages      = row[0]
    avg_latency_ms      = row[1]
    total_input_tokens  = row[2]
    total_output_tokens = row[3]
    unanswered          = row[4]

    estimated_cost = (
        total_input_tokens  * INPUT_PRICE_PER_TOKEN +
        total_output_tokens * OUTPUT_PRICE_PER_TOKEN
    )

    return {
        "bot_id":                    bot_id,
        "total_messages":            total_messages,
        "average_latency_ms":        round(avg_latency_ms, 2),
        "estimated_token_cost_usd":  round(estimated_cost, 6),
        "unanswered_questions":      unanswered,
    }
