"""BookRec: 5-қатысушының тестілеуі. Run: python bookrec_testing.py
Place books.csv next to this script. Outputs are saved in bookrec_test_results/.
This is an independent TF-IDF baseline, not verification of the missing recommender.py.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'bookrec_test_results'
OUT.mkdir(exist_ok=True)
p = ROOT / 'books.csv'
if not p.exists():
    raise SystemExit('books.csv табылмады. GitHub-тан books.csv файлын жүктеп, осы скриптпен бір папкаға салыңыз.')
df = pd.read_csv(p).fillna('')
required = {'book_id', 'title', 'author', 'genre', 'genre_group'}
if not required.issubset(df.columns):
    raise SystemExit('Міндетті бағандар жоқ: ' + ', '.join(sorted(required-set(df.columns))))
for c in ('title','author','genre','genre_group','description'):
    if c not in df: df[c]=''
    df[c] = df[c].astype(str)
text = (df['title']+' '+df['author']+' '+df['description']+' '+df['genre']).str.strip()
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,5))
X = vectorizer.fit_transform(text)

# Three real catalog examples, spanning genre groups where available.
examples = ['Абай жолы: 1-том', 'Ақбілек', 'Менің атым Қожа']
results = []
for title in examples:
    matches = df.index[df.title.str.casefold()==title.casefold()].tolist()
    if not matches:
        print('Каталогта жоқ:', title)
        continue
    idx=matches[0]
    scores=cosine_similarity(X[idx],X).ravel()
    scores[idx]=-1
    top=np.argsort(-scores)[:5]
    truth=df.iloc[idx]['genre_group']
    for rank,j in enumerate(top,1):
        row=df.iloc[j]
        results.append({'test_input':title,'input_group':truth,'rank':rank,
                        'recommended_title':row['title'],'recommended_author':row['author'],
                        'recommended_group':row['genre_group'],
                        'similarity':round(float(scores[j]),4),
                        'relevant_same_genre_group':int(row['genre_group']==truth)})
r=pd.DataFrame(results)
if not r.empty:
    r.to_csv(OUT/'recommendations_3_tests.csv',index=False,encoding='utf-8-sig')
    summary=r.groupby('test_input',sort=False).agg(relevant=('relevant_same_genre_group','sum'),n=('rank','count'))
    summary['precision_at_5']=summary['relevant']/5
    summary.to_csv(OUT/'precision_at_5.csv',encoding='utf-8-sig')
    print('\nҮШ ТЕСТ — Precision@5 (бір жанр тобына сәйкестік):\n',summary.to_string())
else:
    print('Үш тестке қажетті кітаптар табылмады.')

# KMeans is evaluated against existing catalog genre groups, not held-out labels.
if len(df)>5 and df['genre_group'].nunique()>=2:
    k=df['genre_group'].nunique()
    model=KMeans(n_clusters=k,random_state=42,n_init=10)
    clusters=model.fit_predict(X)
    df['cluster']=clusters
    ct=pd.crosstab(df['cluster'],df['genre_group'])
    ct.to_csv(OUT/'cluster_distribution.csv',encoding='utf-8-sig')
    ari=adjusted_rand_score(df['genre_group'],clusters)
    sil=silhouette_score(X,clusters,metric='cosine') if len(set(clusters))>1 else float('nan')
    print(f'\nKMeans: k={k}, ARI={ari:.4f}, cosine silhouette={sil:.4f}')
    print('\nКластерлердің жанр бойынша таралуы:\n',ct.to_string())
    (OUT/'metrics.txt').write_text(f'ARI={ari:.4f}\ncosine_silhouette={sil:.4f}\n',encoding='utf-8')

# Negative case: non-existent title lookup should yield no results.
q='БұлКітапКаталогтаЖоқ_12345'
not_found=df[~df.title.str.contains(q,case=False,regex=False)]
print('\nҚате жағдайы: жоқ кітап атауы -> дәл сәйкестік табылмайды:',not df.title.str.contains(q,case=False,regex=False).any())
print('Нәтижелер:',OUT)
print('Ескерту: бұл — қолда бар CSV бойынша тәуелсіз тест, сайттың нақты recommender.py нәтижесі емес.')
