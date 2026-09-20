import os
import sys
import feedparser
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Sources divisées par langue
SOURCES = {
    "FR": {
        "ANSSI": "https://www.ssi.gouv.fr/actualites/flux-rss/",
        "Cyberveille": "https://cyberveille.fr/feed/",
        "Zataz": "https://www.zataz.com/feed/"
    },
    "EN": {
        "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
        "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
        "Cybersecurity News": "https://cybersecuritynews.com/feed/",
        "Reddit CyberSecurity": "https://www.reddit.com/r/cybersecurity/.rss",
    }
}

DB_FILE = "sent_articles.txt"


def send_telegram_msg(text):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=20)
    except Exception as e:
        print(f"Erreur Telegram : {e}")


def load_sent_articles():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()


def save_sent_article(link):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")


def main():
    print("Démarrage du bot Multilingue...")
    if not TOKEN or not CHAT_ID:
        sys.exit(1)

    sent_articles = load_sent_articles()
    count = 0

    for lang, sources in SOURCES.items():
        emoji_lang = "🇫🇷" if lang == "FR" else "🇬🇧"
        for source_name, url in sources.items():
            print(f"Scan {lang} - {source_name}...")
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    link = entry.link
                    if link not in sent_articles:
                        title = entry.title
                        message = (
                            f"{emoji_lang} *ALERTE CYBER {lang}*\n\n"
                            f"📰 *{title}*\n\n"
                            f"🔗 [Lire l'article]({link})\n\n"
                            f"📌 Source: {source_name}"
                        )
                        send_telegram_msg(message)
                        save_sent_article(link)
                        sent_articles.add(link)
                        count += 1
            except Exception as e:
                print(f"Erreur {source_name} : {e}")

    print(f"Terminé. {count} articles envoyés.")


if __name__ == "__main__":
    main()
