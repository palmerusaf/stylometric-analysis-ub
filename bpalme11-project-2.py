from bs4 import BeautifulSoup
import pandas as pd
import re


# https://www.thetedkarchive.com/library/theo-slade-the-bombings-communications-of-ted-kaczynski-as-part-of-his-terror-campaign
# extract udocs from html

df = pd.DataFrame(columns=["docType", "rawTxt"])
with open("./u-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")
pTags = soup.find_all("p")
count = 1
for p in pTags:
    if not p.get_text(strip=True).startswith("Ted:"):
        continue
    blk = p.find_next("blockquote")
    if not blk:
        continue
    blkText = blk.get_text(strip=True, separator=" ")
    df.loc[len(df)] = ["U", blkText]

# https://www.thetedkarchive.com/library/ted-kaczynski-david-kaczynski-letters-to-from-david-kaczynski
# extract tdocs from html
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
    df.loc[len(df)] = ["T", contents]

# darwin letters for a control
with open("./darwin.html") as f:
    soup = BeautifulSoup(f, "html.parser")
    txt = soup.get_text(strip=True, separator=" ")
    df.loc[len(df)] = ["C", txt]


# clean docs

stopWords = {
    "the",
    "and",
    "is",
    "to",
    "of",
    "a",
    "in",
    "that",
    "it",
    "with",
    "as",
    "for",
    "was",
    "on",
    "be",
    "at",
    "by",
    "an",
    "this",
    "which",
    "or",
    "from",
    "but",
    "not",
}


def clean(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s,.!?]", " ", text)
    text = re.sub(r"\.+", ".", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in stopWords]
    return " ".join(tokens)


df["cleanTxt"] = df["rawTxt"].apply(clean)


def avgSent(text):
    sents = re.split(r"[.!?]", text)
    lengths = [len(s.split()) for s in sents]
    return sum(lengths) / len(lengths) if lengths else 0


df["avgSent"] = df["cleanTxt"].apply(avgSent)
