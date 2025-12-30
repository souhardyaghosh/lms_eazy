from flask import Flask, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# --- CONFIGURATION ---
USERNAME = "23BLC1064"
PASSWORD = "#Babai2395"
URL_LOGIN = "https://lms.vit.ac.in/login/index.php"

# HTML TEMPLATE (The "Website" Look)
# This includes CSS for a beautiful, modern table.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VIT Course Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; padding: 20px; }
        h1 { text-align: center; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #007bff; color: white; text-transform: uppercase; font-size: 0.9em; }
        tr:hover { background-color: #f1f1f1; }
        .code { font-weight: bold; color: #0056b3; }
        .teacher { font-size: 0.9em; color: #555; }
        .loading { text-align: center; font-size: 1.5em; color: #666; padding: 50px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 My Course Dashboard</h1>
        {% if courses %}
            <table>
                <thead>
                    <tr>
                        <th>Course Code</th>
                        <th>Course Name</th>
                        <th>Teachers / Faculty</th>
                    </tr>
                </thead>
                <tbody>
                    {% for course in courses %}
                    <tr>
                        <td class="code">{{ course.code }}</td>
                        <td>{{ course.name }}</td>
                        <td class="teacher">{{ course.teachers }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div class="loading">Loading data from LMS... Please wait...</div>
        {% endif %}
    </div>
</body>
</html>
"""

def scrape_lms():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") 
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    course_data = []

    try:
        # LOGIN
        driver.get(URL_LOGIN)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.ID, "loginbtn").click()

        # DASHBOARD
        wait.until(EC.url_contains("/my/"))
        try: wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card.dashboard-card")))
        except: pass
        time.sleep(3)

        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='course/view.php?id=']")
        seen_ids = set()
        temp_list = []

        # 1. Collect Links
        for link in links:
            url = link.get_attribute("href")
            text = link.text.strip()
            if url and "id=" in url and url not in seen_ids:
                clean_text = text.replace("Course is starred", "").replace("Course name", "").strip()
                if "(" in clean_text and ")" in clean_text:
                    try:
                        name_part, code_part = clean_text.rsplit('(', 1)
                        c_name = name_part.strip()
                        c_code = code_part.replace(')', '').strip()
                        seen_ids.add(url)
                        temp_list.append({'code': c_code, 'name': c_name, 'url': url})
                    except: continue

        # 2. Visit Each Course
        for course in temp_list:
            driver.get(course['url'])
            try: WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "course-content")))
            except: pass
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            headers = soup.select("h3.sectionname, .sectionname")
            found_names = []
            
            for h in headers:
                h_text = h.get_text(strip=True)
                if any(x in h_text for x in ["Dr.", "Prof.", "Faculty", "Mr.", "Ms."]):
                    if h_text not in found_names:
                        found_names.append(h_text)
            
            teacher_str = " | ".join(found_names) if found_names else "Not Listed"
            course_data.append({'code': course['code'], 'name': course['name'], 'teachers': teacher_str})

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    return course_data

@app.route('/')
def home():
    # When you open the website, it runs the scraper
    print("User requested page. Starting scraper...")
    data = scrape_lms()
    return render_template_string(HTML_TEMPLATE, courses=data)

if __name__ == '__main__':
    print("Server starting on http://127.0.0.1:5000")
    app.run(debug=True)