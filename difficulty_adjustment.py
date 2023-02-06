import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from utils import bits_to_target


def get_bits():
    db_name = "./data/bc.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get the bits history
    query = "SELECT height, bits, timestamp FROM block_headers GROUP BY bits ORDER BY height ASC"
    cursor.execute(query)
    conn.commit()
    bits_history = cursor.fetchall()

    # Get the current bits
    query_current = "SELECT height, bits FROM block_headers ORDER BY height DESC LIMIT 1"
    bits_current = cursor.execute(query_current)
    conn.commit()
    bits_current = bits_current.fetchone()

    return bits_history, bits_current


history, current = get_bits()


df = pd.DataFrame(history, columns=["height", "bits", "timestamp"])
df["target"] = df["bits"].apply(bits_to_target)


periods = pd.DataFrame()
periods["time"] = df["timestamp"].diff().dropna() / 60
periods["blocks_per_min"] = 50 / periods["time"]
periods["difficulty"] = (df["target"][0] / df["target"]).shift(1)
periods["blocks"] = (df["height"] - 50).apply(str) + \
    "-" + (df["height"] - 1).apply(str)

print(periods)
print()
print(
    f"Current difficulty: {df['target'][0] / bits_to_target(current[1])} at height {current[0]}")

plt.figure(figsize=(12, 8))
# Plot the difficulty as bars
plt.bar(periods["blocks"], periods["difficulty"], width=0.8)
plt.xlabel("Blocks")
plt.ylabel("Difficulty")
plt.xticks(rotation=45, ha='right', rotation_mode="anchor")

# Plot the blocks per minute as a line in the same figure
plt.twinx()
plt.plot(periods["blocks"], periods["blocks_per_min"], color="red")

plt.axhline(y=1, color="black", linestyle="--")
plt.text(0, 1, "1 block per minute", color="black",
         va="bottom", fontweight="bold")

plt.ylabel("Blocks per minute")
plt.title("Difficulty and blocks per minute")
plt.savefig("difficulty_and_blocks_per_min.png")
