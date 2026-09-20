import feedparser
  import requests
  import os

  # --- CONFIGURATION ---
  TOKEN = os.environ.get('TELEGRAM_TOKEN')
  CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

  # Liste des flux RSS à surveiller (Cyber & Tech)
  SOURCES = {
      "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
      "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
      "Cybersecurity News": "https://cybersecuritynews.com/feed/",
      "Reddit CyberSecurity": "https://www.reddit.com/r/cybersecurity/.rss"
  }

  DB_FILE = "sent_articles.txt"

  def send_telegram_msg(text):
      url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
      payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
      requests.post(url, json=payload)

  def load_sent_articles():
      if os.path.exists(DB_FILE):
          with open(DB_FILE, "r") as f:
              return set(f.read().splitlines())
      return set()

  def save_sent_article(link):
      with open(DB_FILE, "a") as f:
          f.write(link + "\n")

  def main():
      sent_articles = load_sent_articles()

      for source_name, url in SOURCES.items():
          print(f"Vérification de {source_name}...")
          feed = feedparser.parse(url)

          for entry in feed.entries[:5]: # On prend les 5 derniers articles
              link = entry.link
              if link not in sent_articles:
                  title = entry.title
                  message = f"🚨 *ALERTE CYBER* 🚨\n\n📖 *{title}*\n\n🔗 [Lire l'article]({link})\n\n📡 Source: {source_name}"
                  send_telegram_msg(message)
                  save_sent_article(link)
                  sent_articles.add(link)

  if __name__ == "__main__":
      main()
