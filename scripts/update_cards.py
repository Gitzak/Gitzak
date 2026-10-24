"""Render both GitHub cards in one shared, fixed-size SVG canvas."""
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
def tag(name):
    return f"{{{NS}}}{name}"

common = "username=Gitzak&hide_border=true&bg_color=0D1117&title_color=BEF264&icon_color=BEF264&text_color=C9D1D9&card_width=467&disable_animations=true"
urls = [
    "https://github-readme-stats.vercel.app/api?" + common + "&show_icons=true&hide_rank=true",
    "https://github-readme-stats.vercel.app/api/top-langs/?" + common + "&layout=compact&langs_count=8",
]
root = ET.Element(tag("svg"), {"width": "960", "height": "236", "viewBox": "0 0 960 236", "role": "img", "aria-labelledby": "cards-title"})
ET.SubElement(root, tag("title"), {"id": "cards-title"}).text = "GitHub stats and most used languages — matching cards"
for index, url in enumerate(urls):
    request = Request(url, headers={"User-Agent": "Gitzak-profile-cards"})
    with urlopen(request, timeout=60) as response:
        source = ET.fromstring(response.read())
    if "svg" not in source.tag or "Something went wrong" in "".join(source.itertext()):
        raise RuntimeError("Stats provider returned an invalid card")
    x = index * 492
    # Identical physical cards: 468 x 236, 24px gutter, 24px inset.
    ET.SubElement(root, tag("rect"), {"x": str(x + 0.75), "y": ".75", "width": "466.5", "height": "234.5", "rx": "12", "fill": "#0D1117", "stroke": "#303B26", "stroke-width": "1.5"})
    # Preserve original type size; both source viewports use the same coordinates.
    source.set("x", str(x + 4))
    source.set("y", "10")
    source.set("width", "460")
    source.set("height", "216")
    source.set("viewBox", "0 0 467 220")
    source.set("preserveAspectRatio", "xMinYMin meet")
    # Prefix IDs to prevent collisions between embedded cards.
    for element in source.iter():
        if "id" in element.attrib:
            element.set("id", f"card{index}-" + element.get("id"))
        for key, value in list(element.attrib.items()):
            if "url(#" in value:
                element.set(key, value.replace("url(#", f"url(#card{index}-"))
    root.append(source)
Path("assets/github-cards.svg").write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
