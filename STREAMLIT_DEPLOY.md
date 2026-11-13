# Streamlit Community Cloud-та жариялау

Бұл файл сайтты `https://<таңдалған-бос-атау>.streamlit.app` доменінде іске қосуға арналған. Домен жарияланғаннан кейін ғана нақты жұмыс істейді.

1. https://share.streamlit.io сайтына GitHub-тағы **Arai747** аккаунтыңызбен кіріңіз.
2. **Create app → Yup, I have an app** таңдаңыз.
3. Мына мәндерді енгізіңіз:

| Өріс | Мәні |
|---|---|
| Repository | `Arai747/kazakh-books-recommender` |
| Branch | `main` |
| Main file path | `app.py` |
| Advanced settings → Python | `3.12` |
| App URL | Қолжетімді өз атауыңыз; мысалы `bookrec-arai747` |

4. **Deploy** басыңыз. Алғашқы орнату біткен соң берілген `*.streamlit.app` сілтемесін көшіріңіз.

Жұмыс тармағы: `codex/streamlit-backend-reading-list`. Негізгі жарияланатын нұсқа — `main`. Бар қосымша main тармағын бақыласа, GitHub жаңартылғаннан кейін Streamlit оны автоматты қайта жинайды.

Бар қосымшаның мекенжайы: https://kazakh-books-recommender-wwffat9e4d9r7dlven67wk.streamlit.app . Қолжетімділік пен соңғы жинақ күйі Streamlit панелінен тексеріледі.

## Жергілікті іске қосу

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows-та алдыңғы команданың орнына: .venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Алғаш ашылғанда SQLite базасы автоматты түрде `integrated-site/bookrec.db` ішінде жасалады. Өз жолыңыз үшін `BOOKREC_DB_PATH` орта айнымалысын беріңіз.

## Деректерді сақтау

Жеке кодпен сол базада сақталған тізім мен таңдауды басқа сеанста қалпына келтіруге болады. Кодты жеке сақтаңыз.

Community Cloud жергілікті дискідегі SQLite файлының ұзақ сақталуына кепілдік бермейді: қайта іске қосу/қайта орналастыру кезінде ол жоғалуы мүмкін. Жергілікті компьютерде файл сақталғанша деректер қалады. Cloud-та тұрақты сақтау қажет болса, дайын PostgreSQL қолдауы үшін **Advanced settings → Secrets** ішінде `DATABASE_URL` мәнін орнатыңыз. Құпия мәнді GitHub-қа салмаңыз.

Ресми нұсқаулықтар:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
