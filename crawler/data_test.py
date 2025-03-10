from fetch_article_links import fetch_all_articles

# ✅ Retain only the "Earth" category from the fetched article links
filtered_data = {"Earth": fetch_all_articles().get("Earth", [])}

# ✅ Print the final filtered result
print(filtered_data)

