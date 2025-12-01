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
    if h4Text.startswith("From Ted to") and "(T-" in h4Text:
        contents = []
        for sib in h4.next_siblings:
            if sib.name == "h4" or (sib.name == "h3" and sib.get_text() == "Sources"):
                break
            contents.append(sib.get_text(strip=True, separator=" "))
        rows.append(("Ted Letters", " ".join(contents)))
    if h4Text.startswith("From Dave"):
        contents = []
        for sib in h4.next_siblings:
            if sib.name == "h4" or (sib.name == "h3" and sib.get_text() == "Sources"):
                break
            contents.append(sib.get_text(strip=True, separator=" "))
        rows.append(("Dave Letters", " ".join(contents)))


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


def clean(text):
    text = text.lower()
    tokens = text.split()
    return " ".join(tokens)


df["cleanTxt"] = df["rawTxt"].apply(clean)

# TF-IDF TO 3D PCA
# good for content similarity
# https://www.geeksforgeeks.org/machine-learning/understanding-tf-idf-term-frequency-inverse-document-frequency/
# https://www.ibm.com/think/topics/principal-component-analysis
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
    title="TF-IDF 3D PCA Simple Bag of Words",
)

fig.show()


# avg sent len box whisker plot
def avgSent(text):
    sents = re.split(r"[.!?]", text)
    lengths = [len(s.split()) for s in sents]
    return sum(lengths) / len(lengths) if lengths else 0


df["Avg Sent Length"] = df["cleanTxt"].apply(avgSent)

# plotly box whisker on avg sent for each doc type
fig = px.box(
    df,
    x="Doc Type",
    y="Avg Sent Length",
    title="Average Sentence Length by Document Type",
    color="Doc Type",
    points="all",
)

# In his study, Reference GrieveGrieve (2007) finds that character n-grams (up to about 6-grams) can be useful as authorship markers along with various measures of word and punctuation distribution, and shows how with a decreasing number of candidate authors in a closed set, other features, including some measures of lexical richness and average word and sentence length, might have some role to play, but generally lack a strong predictive power.

fig.show()
# https://www.cambridge.org/core/elements/idea-of-progress-in-forensic-authorship-analysis/6A4F7668B4831CCD7DBF74DECA3EBA06
X = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 6),
    min_df=2,
    max_features=10000,
).fit_transform(df["rawTxt"])

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
    title="TF-IDF 3D PCA 6-grams Grieve (2007)",
)
fig.show()

# legit stylometry
# https://www.nature.com/articles/s41599-025-05986-3
# https://fastdatascience.com/natural-language-processing/fast-stylometry-python-library/
# burrows delta mds scatter
