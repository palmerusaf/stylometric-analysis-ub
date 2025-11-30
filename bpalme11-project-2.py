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
    print(RED)
    print(p)
    print(RESET)
    blkQ = p.find_next("blockquote")
    if not blkQ:
        continue
    print(GREEN)
    print(blkQ)
    print(RESET)
    uDocs.append(blkQ.get_text(strip=True))
