from bs4 import BeautifulSoup


# https://www.thetedkarchive.com/library/theo-slade-the-bombings-communications-of-ted-kaczynski-as-part-of-his-terror-campaign
# extract udocs from html
uDocs = []
with open("./u-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")
pTags = soup.find_all("p")
for p in pTags:
    if not p.get_text(strip=True).startswith("Ted:"):
        continue
    blk = p.find_next("blockquote")
    if not blk:
        continue
    blkText = blk.get_text(strip=True, separator=" ")
    uDocs.append(blkText)

# https://www.thetedkarchive.com/library/ted-kaczynski-david-kaczynski-letters-to-from-david-kaczynski
# extract tdocs from html
tDocs = []
with open("./t-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")
h4s = soup.find_all("h4")
for h4 in h4s:
    h4Text = h4.get_text()
    if not h4Text.startswith("From Ted to") or "(T-" not in h4Text:
        continue
    contents = ""
    for sib in h4.next_siblings:
        if sib.name == "h4" or sib.name == "h3" and sib.get_text() == "Sources":
            break
        contents += sib.get_text(strip=True, separator=" ")
    tDocs.append(contents)
