from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv, json



opts = Options()
opts.add_argument("--log-level=3")
opts.add_experimental_option("excludeSwitches", ["enable-logging"])

tmp_profile = tempfile.mkdtemp()
opts.add_argument(f"--user-data-dir={tmp_profile}")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

driver.get("https://oldschool.runescape.com/")

print(driver.title)

try:
    accept = wait.until(EC.element_to_be_clickable(
        (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
    ))
    accept.click()
except:
    # fallback: sometimes it’s a different layout; ignore if it doesn't appear
    pass


highscores = driver.find_element(By.ID, "osnav-hiscores")
highscores.click()

WebDriverWait(driver, 15).until(lambda d: "hiscore" in d.current_url.lower())

search = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.NAME, "user1"))
)

search.clear()
search.send_keys("Arihant")
search.send_keys(Keys.ENTER)

# wait until results table is there
wait.until(EC.presence_of_element_located((By.XPATH, "//a[normalize-space()='Overall']")))

# grab every skill row (rows that have a skill link)
rows = driver.find_elements(By.XPATH, "//*[@id='contentHiscores']//tr[td//a]")

data = []
for r in rows:
    # skip icon/empty cells
    tds = r.find_elements(By.XPATH, "./td[normalize-space()]")
    if len(tds) < 4:
        continue

    vals = [td.get_attribute("textContent").strip() for td in tds[:4]]
    skill, rank, level, xp = vals

    data.append({"skill": skill, "rank": rank, "level": level, "xp": xp})

# save files named after the player
player = "Arihant"
csv_path = f"{player}_hiscores.csv"
json_path = f"{player}_hiscores.json"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["skill", "rank", "level", "xp"])
    w.writeheader()
    w.writerows(data)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Saved {len(data)} rows to {csv_path} and {json_path}")


input("Press Enter to close...")
driver.quit()