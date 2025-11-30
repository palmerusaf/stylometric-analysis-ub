from bs4 import BeautifulSoup

with open("./u-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")

uDocs = []
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"  # Resets all formatting
pTags = soup.find_all("p")
for p in pTags:
    if not p.get_text(strip=True).startswith("Ted:"):
        continue
    blkQ = p.find_next("blockquote")
    if not blkQ:
        continue
    uDocs.append(blkQ.get_text(strip=True))

with open("./t-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")
tDocs = []

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
    # print(RED)
    # print(h4Text)
    # print(RESET)
    # print(GREEN)
    # print(contents)
    # print(RESET)
    tDocs.append(contents)
