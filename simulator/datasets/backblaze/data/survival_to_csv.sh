#!/bin/sh
if [ $# -eq 0 ]; then
    echo "Usage: $0 input.db" >&2
    exit 1
fi

INPUT="$1"
OUTPUT="${INPUT%.*}.csv"

# Export data to a csv file in a simplified format.
sqlite3 -header -csv "$INPUT" > "$OUTPUT" <<_END_
SELECT
  model,
  CAST(julianday(expiry) - julianday(birthday) AS INT) AS age,
  -- Censored if it expires on the last day.
  censored,
  -- Use natural numbers for dates.
  CAST(julianday(birthday) - MIN(julianday(birthday)) OVER() AS INT) AS birthday
FROM summary_drive_stats where exclude = 0;
_END_

# Replace group names with shorter names.
sed -i -f - "$OUTPUT" <<_END_
  s/ST4000DM000/S4/
  s/ST8000DM002/S8C/
  s/ST8000NM0055/S8E/
  s/ST12000NM0007/S12E/
  s/"HGST HMS5C4040ALE640"/H4A/
  s/"HGST HMS5C4040BLE640"/H4B/
  s/"HGST HUH721212ALN604"/H12E/
_END_

# Censor failures flagged as anomalies.
#sed -i -f - "$OUTPUT" <<_END_
#  s/H4B,234,0,1330/H4B,234,1,1330/
#  s/H4B,379,0,1185/H4B,379,1,1185/
#  s/S12E,21,0,1861/S12E,21,1,1861/
#_END_

