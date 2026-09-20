import feedparser
  import requests
  import os
  import sys

  # --- CONFIGURATION ---
  TOKEN = os.environ.get('TELEGRAM_TOKEN')
  CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

  # Liste des flux RSS à surveiller
  SOURCES = {
      "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
      "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
      "Cybersecurity News": "https://cybersecuritynews.com/feed/",
      "Reddit CyberSecurity": "https://www.reddit.com/r/cybersecurity/.rss"
  }

  DB_FILE = "sent_articles.txt"

  def send_telegram_msg(text):
      if not TOKEN or not CHAT_ID:
          print("ERREUR : TOKEN ou CHAT_ID manquant dans les secrets GitHub !")
          return
      url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
      payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
      try:
          response = requests.post(url, json=payload)
          response.raise_for_status()
      except Exception as e:
          print(f"Erreur lors de l'envoi Telegram : {e}")

  def load_sent_articles():
      if os.path.exists(DB_FILE):
          with open(DB_FILE, "r") as f:
              return set(f.read().splitlines())
      print("Création d'un nouveau fichier de suivi...")
      return set()

  def save_sent_article(link):
      with open(DB_FILE, "a") as f:
          f.write(link + "\n")

  def main():
      print("Démarrage du bot...")

      if not TOKEN or not CHAT_ID:
          print("ERREUR CRITIQUE : Les secrets TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID sont vides.")
          sys.exit(1)

      sent_articles = load_sent_articles()
      count = 0

      for source_name, url in SOURCES.items():
          print(f"Scan de {source_name}...")
          try:
              feed = feedparser.parse(url)
              for entry in feed.entries[:5]:
                  link = entry.link
                  if link not in sent_articles:
                      title = entry.title
                      message = f"🚨 *ALERTE CYBER* 🚨\n\n📖 *{title}*\n\n🔗 [Lire l'article]({link})\n\n📡 Source: {source_name}"
                      send_telegram_msg(message)
                      save_sent_article(link)
                      sent_articles.add(link)
                      count += 1
          except Exception as e:
              print(f"Erreur avec la source {source_name} : {e}")

      print(f"Terminé. {count} nouveaux articles envoyés.")

  if __name__ == "__main__":
      main()
