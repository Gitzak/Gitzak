import datetime as dt
import html
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        date, level = attrs.get("data-date"), attrs.get("data-level")
        if date and level is not None:
            self.days[dt.date.fromisoformat(date)] = int(level)

request = Request("https://github.com/users/Gitzak/contributions", headers={"User-Agent": "Gitzak-profile-calendar"})
with urlopen(request, timeout=45) as response:
    page = response.read().decode()
calendar = Calendar()
calendar.feed(page)
if len(calendar.days) < 300:
    raise RuntimeError("Incomplete contribution calendar; keeping the existing graph")
days = sorted(calendar.days)
start = days[0] - dt.timedelta(days=(days[0].weekday() + 1) % 7)
colors = ["#161B22", "#34471D", "#64852D", "#94BF45", "#BEF264"]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="210" viewBox="0 0 900 210" role="img" aria-labelledby="title desc">',
'<title id="title">Gitzak contribution calendar</title>',
'<desc id="desc">Daily contribution intensity from the GitHub profile calendar. Brighter lime indicates more activity.</desc>',
'<rect width="900" height="210" rx="10" fill="#0D1117"/>',
'<g font-family="Arial,Helvetica,sans-serif"><text x="24" y="30" fill="#BEF264" font-size="16" font-weight="600">Contribution activity</text>']
for date in days:
    offset = (date - start).days
    x, y = 36 + (offset // 7) * 16, 55 + (offset % 7) * 16
    level = calendar.days[date]
    parts.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{colors[level]}"><title>{date}: activity level {level} of 4</title></rect>')
parts.append(f'<text x="24" y="192" fill="#8B949E" font-size="11">GitHub contribution intensity · Updated {dt.datetime.now(dt.timezone.utc).date()} UTC</text>')
parts.append('<text x="710" y="192" fill="#8B949E" font-size="11">Less</text>')
for i, color in enumerate(colors):
    parts.append(f'<rect x="{742 + i * 16}" y="182" width="12" height="12" rx="2" fill="{color}"/>')
parts.append('<text x="830" y="192" fill="#8B949E" font-size="11">More</text></g></svg>')
Path("assets").mkdir(exist_ok=True)
Path("assets/contributions.svg").write_text("".join(parts), encoding="utf-8")
