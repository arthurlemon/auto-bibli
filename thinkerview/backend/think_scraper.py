import requests
from selectolax.parser import HTMLParser


def parse_date(date_str):
    months = {
        "janvier": "01",
        "février": "02",
        "mars": "03",
        "avril": "04",
        "mai": "05",
        "juin": "06",
        "juillet": "07",
        "août": "08",
        "septembre": "09",
        "octobre": "10",
        "novembre": "11",
        "décembre": "12",
    }

    day, month, year = date_str.split()
    month = months[month.lower()]
    return f"{year}-{month}-{day.zfill(2)}"


def get_youtube_url(interview_url):
    response = requests.get(interview_url)
    parser = HTMLParser(response.text)
    iframe = parser.css_first("iframe")
    if iframe:
        return iframe.attributes.get("src", "")
    return None


def parse_interviewees(description):
    interviewees = []
    for line in description.split("\n"):
        if "," in line:
            name, position = line.split(",", 1)
            interviewees.append(
                {"full_name": name.strip(), "position": position.strip()}
            )
    return interviewees


def scrape_page(url, conn):
    response = requests.get(url)
    parser = HTMLParser(response.text)

    interviews = parser.css("div.post.box")

    for interview in interviews:
        title = interview.css_first("h4.post-title").text().strip()
        url = interview.css_first("h4.post-title a").attributes["href"]
        date_str = interview.css_first("span.date").text().strip()
        date = parse_date(date_str)

        description = interview.css_first("p").text().strip()
        categories = [cat.text() for cat in interview.css("span.category a")]
        thumbnail = interview.css_first("img").attributes.get("src", "")

        youtube_url = get_youtube_url(url)
        interviewees = parse_interviewees(description)
        with conn.cursor() as cur:
            cur.execute(
                """
            INSERT INTO interviews
            (title, date, description, categories, url, thumbnail_url, youtube_url, interviewees)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """,
                (
                    title,
                    date,
                    description,
                    categories,
                    url,
                    thumbnail,
                    youtube_url,
                    interviewees,
                ),
            )

    next_page = parser.css_first('div.pagination a[href*="page/2"]')
    return next_page.attributes["href"] if next_page else None
