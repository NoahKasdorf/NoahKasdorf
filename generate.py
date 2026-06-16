#!/usr/bin/env python3
"""Generate retro green terminal neofetch GIF.
Uses live GitHub stats when GITHUB_TOKEN is set (as in the Action); falls back
to placeholder numbers locally so the layout can be previewed without a token.
"""
import os, json, urllib.request, datetime
import gifos
from gifos.utils import fetch_github_stats, calc_age

USER = "NoahKasdorf"

# ---- ANSI helpers (colors come from the 'hacker' scheme in the TOML) ----
RESET = "\x1b[0m"
HEAD  = "\x1b[1;32m"   # bright green
KEY   = "\x1b[36m"     # pale green (mapped to 'cyan' in scheme)
VAL   = "\x1b[32m"     # green

def kv(label, value):
    return f"{KEY}{label:<11}{RESET}{VAL}{value}{RESET}"

# ---- gather stats ----
token = os.environ.get("GITHUB_TOKEN")
member = "n/a"
try:
    # account age (public endpoint; works with or without token)
    hdr = {"User-Agent": "gifos"}
    if token: hdr["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/users/{USER}", headers=hdr)
    created = json.load(urllib.request.urlopen(req, timeout=15))["created_at"]
    d = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
    age = calc_age(d.day, d.month, d.year)
    member = f"{age.years}y {age.months}m"
except Exception as e:
    print("age fetch skipped:", e)

if token:
    s = fetch_github_stats(USER, include_all_commits=True)
    commits   = s.total_commits_all_time
    repos     = s.total_repo_contributions
    langs     = ", ".join(n for n, _ in s.languages_sorted[:6]) or "n/a"
else:
    print("No GITHUB_TOKEN -> using placeholder numbers for local preview")
    commits, repos = 1284, 37, 21, 18
    rank, langs = "A+ (top 6%)", "Python, TypeScript, Java, C"

# ---- build the terminal ----
t = gifos.Terminal(width=760, height=500, xpad=14, ypad=12)
t.set_bg_color("#060a06")
t.set_txt_color("#33ff5e")

# boot
t.gen_typing_text("[ ok ]  booting noah-os ...", row_num=1)
t.gen_text(text="[ ok ]  mounting /dev/curiosity", row_num=2)
t.gen_text(text="[ ok ]  starting interactive shell", row_num=3)

# whoami
t.gen_typing_text("noah@github:~$ whoami", row_num=5)
t.gen_text(text="Noah Kasdorf", row_num=6)

# about
t.gen_typing_text("noah@github:~$ cat about.txt", row_num=7)
t.gen_text(
    text="Generally curious, always up for learning something new. When not at a keyboard: cycling, bouldering, long trails, and science fiction.",
    row_num=8,
)

# neofetch
t.gen_typing_text("noah@github:~$ neofetch", row_num=10)
t.gen_text(text=f"{HEAD}noah@github{RESET}", row_num=11)
t.gen_text(text="-----------", row_num=12)
t.gen_text(text=kv("OS:",        "Carleton MCS - Data Science & AI"), row_num=13)
t.gen_text(text=kv("Edu:",       "BCS Honours - AI & Machine Learning"), row_num=14)
t.gen_text(text=kv("Member:",    member), row_num=15)
t.gen_text(text=kv("Commits:",   commits), row_num=16)
t.gen_text(text=kv("Repos:",     repos), row_num=19)
t.gen_text(text=kv("Langs:",     langs), row_num=21)
# neofetch color swatch
swatch = "".join(f"\x1b[4{i}m   " for i in range(0, 8)) + RESET
t.gen_text(text=swatch, row_num=23)

# hold the final frame so it lingers before the loop restarts
for _ in range(1000):
    t.clone_frame()

t.gen_gif()
print("done")
