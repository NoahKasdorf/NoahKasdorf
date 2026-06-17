import os, json, urllib.request, datetime
import gifos
from gifos.utils import fetch_github_stats, calc_age

USER = "NoahKasdorf"

RESET = "\x1b[0m"
HEAD = "\x1b[1;32m"  # bright green
KEY = "\x1b[36m"  # pale green
VAL = "\x1b[32m"  # green
AMBER = "\x1b[33m"  # rocket exhaust


def kv(label, value):
    return f"{KEY}{label:<10}{RESET}{VAL}{value}{RESET}"


def gh_get(url, token):
    hdr = {"User-Agent": "gifos"}
    if token:
        hdr["Authorization"] = f"Bearer {token}"
    return json.load(
        urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=15)
    )


# ---- stats ----
token = os.environ.get("GITHUB_TOKEN")
member = "n/a"
try:
    created = gh_get(f"https://api.github.com/users/{USER}", token)["created_at"]
    d = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
    age = calc_age(d.day, d.month, d.year)
    member = f"{age.years}y {age.months}m"
except Exception as e:
    print("age fetch skipped:", e)

if token:
    s = fetch_github_stats(USER, include_all_commits=True)
    commits = s.total_commits_all_time
    langs = ", ".join(n for n, _ in s.languages_sorted[:5]) or "n/a"
    try:
        u = gh_get("https://api.github.com/user", token)
        repos = u.get("public_repos", 0) + u.get("total_private_repos", 0)
    except Exception as e:
        print("repo count fallback:", e)
        repos = s.total_repo_contributions
else:
    print("No GITHUB_TOKEN -> using placeholder numbers for local preview")
    commits, repos = 1284, 37
    langs = "Python, TypeScript, Java, C, R"

# ---- neofetch: ASCII rocket logo (left) + info (right) ----
logo = [
    "       /\\",
    "      /  \\",
    "     /    \\",
    "     |    |",
    "     | GH |",
    "     |    |",
    "    /|    |\\",
    "   / |    | \\",
    "  /__|____|__\\",
    "     |    |",
    "     |    |",
    "     \\/\\/\\/",  # exhaust (index 11) -> amber
]
swatch = "".join(f"\x1b[4{i}m   " for i in range(0, 8)) + RESET
info = [
    f"{HEAD}noah@github{RESET}",
    "-----------",
    kv("Host:", "Carleton University"),
    kv("Masters:", "M.C.S. - Data Science, Analytics & AI"),
    kv("Bachelor:", "B.C.S. - AI & Machine Learning (Hons)"),
    "",
    kv("Member:", member),
    kv("Commits:", commits),
    kv("Repos:", repos),
    kv("Langs:", langs),
    "",
    swatch,
]

# ---- build ----
t = gifos.Terminal(width=760, height=540, xpad=14, ypad=12)
t.set_bg_color("#060a06")
t.set_txt_color("#33ff5e")

t.gen_typing_text("[ ok ]  booting noah-os ...", row_num=1)
t.gen_text(text="[ ok ]  mounting /dev/curiosity", row_num=2)
t.gen_text(text="[ ok ]  starting interactive shell", row_num=3)

t.gen_typing_text("noah@github:~$ whoami", row_num=5)
t.gen_text(text="Noah Kasdorf", row_num=6)
t.gen_typing_text("noah@github:~$ cat about.txt", row_num=7)
t.gen_text(text="Generally curious, always up for learning something new.", row_num=8)
t.gen_text(
    text="Off the clock: cycling, bouldering, long trails, science fiction.", row_num=9
)

t.gen_typing_text("noah@github:~$ neofetch", row_num=11)
for i in range(max(len(logo), len(info))):
    left = (logo[i] if i < len(logo) else "").ljust(16)
    if i == 11:  # colour the exhaust flame
        left = AMBER + left + RESET
    right = info[i] if i < len(info) else ""
    t.gen_text(text=left + right, row_num=12 + i)

for _ in range(500):
    t.clone_frame()

t.gen_gif()
print("done")
