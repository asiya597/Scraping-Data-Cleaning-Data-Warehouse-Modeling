import time, csv, re
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.avito.ma/fr/maroc/appartements-%C3%A0_vendre")

results = []

for page in range(10):

    print(f"Page {page+1}")

    # scroll
    for _ in range(3):
        driver.execute_script("window.scrollBy(0,1000)")
        time.sleep(1)

    cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/appartements/']")

    print("CARDS FOUND:", len(cards))  # 👈 هنا حطها

    for c in cards:
        try:
            text = c.text

                    # -------- TITLE (correct) --------
            title = None
            try:
                title = c.find_element(By.CSS_SELECTOR, "p[title]").text
            except:
                pass

            # -------- PRICE FINAL WORKING --------
            price = None

            try:
                price_element = c.find_element(
                    By.CSS_SELECTOR,
                    "span.sc-3286ebc5-2.PuYkS"
                )

                price_text = price_element.get_attribute("textContent")

                print("RAW PRICE:", repr(price_text))

                # نحيد جميع أنواع spaces
                price_text = re.sub(r"[^\d]", "", price_text)

                if price_text:
                    price = int(price_text)

                print("FINAL PRICE:", price)

            except Exception as e:
                print("PRICE ERROR:", e)


            # location
            location = None
            if "dans" in text:
                location = [l for l in text.split("\n") if "dans" in l]
                location = location[0] if location else None

            # details
            surface = rooms = baths = None
            for l in text.lower().split("\n"):
                if "m²" in l: surface = l
                if "chambre" in l: rooms = l
                if "sdb" in l or "bain" in l: baths = l

            results.append([title, price, location, surface, rooms, baths, c.get_attribute("href")])

        except:
            pass

    # next page
    try:
        driver.find_elements(By.CSS_SELECTOR, "a[href*='?o=']")[-1].click()
        time.sleep(2)
    except:
        break

driver.quit()

# save
with open("avito_data_clean.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["title","price","location","surface","rooms","baths","link"])
    writer.writerows(results)

print("DONE")