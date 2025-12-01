from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd
import re


# https://www.thetedkarchive.com/library/theo-slade-the-bombings-communications-of-ted-kaczynski-as-part-of-his-terror-campaign
# extract udocs from html
rows = []  # collect rows FAST
with open("./u-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")
for p in soup.find_all("p"):
    if not p.get_text(strip=True).startswith("Ted:"):
        continue

    blk = p.find_next("blockquote")
    if not blk:
        continue
    blkText = blk.get_text(strip=True, separator=" ")
    rows.append(("Unabomber", blkText))


# extract tdocs from html
with open("./t-docs.html") as f:
    soup = BeautifulSoup(f, "html.parser")
for h4 in soup.find_all("h4"):
    h4Text = h4.get_text()
    if not h4Text.startswith("From Ted to") or "(T-" not in h4Text:
        continue

    contents = []
    for sib in h4.next_siblings:
        if sib.name == "h4" or (sib.name == "h3" and sib.get_text() == "Sources"):
            break
        contents.append(sib.get_text(strip=True, separator=" "))
    rows.append(("Ted Letters", " ".join(contents)))


# darwin letters for a control
with open("./darwin.html") as f:
    soup = BeautifulSoup(f, "html.parser")

p_tags = soup.find_all("p")

current_letter = None
contents = []

for p in p_tags:
    text = p.get_text(strip=True, separator=" ")

    if text.startswith("LETTER"):
        # save previous letter first
        if current_letter is not None and contents:
            rows.append(("Darwin Control", " ".join(contents)))

        # start new collection
        current_letter = text
        contents = []
        continue

    # inside letter
    if current_letter is not None:
        contents.append(text)

# save last letter
if current_letter is not None and contents:
    rows.append(("Darwin Control", " ".join(contents)))

df = pd.DataFrame(rows, columns=["Doc Type", "rawTxt"])

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


X = TfidfVectorizer(max_features=5000).fit_transform(df["cleanTxt"])

pca = PCA(n_components=3)
pcs = pca.fit_transform(X.toarray())

df["PC1"] = pcs[:, 0]
df["PC2"] = pcs[:, 1]
df["PC3"] = pcs[:, 2]

fig = px.scatter_3d(
    df,
    x="PC1",
    y="PC2",
    z="PC3",
    color="Doc Type",
    title="TF-IDF Squeezed into 3D PCA",
)

fig.show()
