import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.python.org/jobs/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    # Step 1: Get webpage
    html = requests.get(url, headers=headers, timeout=30)
    html.raise_for_status()

    soup = BeautifulSoup(html.text, "html.parser")

    # Step 2: Find jobs container
    job_container = soup.find("ol", class_="list-recent-jobs")

    if not job_container:
        print("Jobs container not found")
        raise ValueError("Jobs container not found")

    jobs = job_container.find_all("li")
    print("Jobs found:", len(jobs))

    # Step 3: Store raw job information
    job_info = []

    for job in jobs:
        job_info.append(" ".join(job.prettify().split()))

    job_df = pd.DataFrame(job_info, columns=["Info"])
    job_df["Info"] = job_df["Info"].replace("", None)
    job_df = job_df.dropna(axis=0, subset=["Info"])

    # Step 4: Save raw data
    file_name = (
        r"C:\Users\mani\OneDrive\Documents\Job_portal\jobs_info_raw.csv"
    )

    try:
        job_df.to_csv(file_name, index=False)
        print("Raw Data Stored Successfully")

    except PermissionError as e:
        print("Permission denied while saving raw data.")
        print("Close the CSV file if it is open in Excel.")
        print("Error:", e)
        raise

    except Exception as e:
        print("Error saving raw data:", e)
        raise

    # Step 5: Extract job information
    job_info = job_df["Info"].to_dict()
    job_info = job_info.values()

    job_titles = []
    companies = []
    posted_dates = []
    locations = []

    for element in job_info:
        try:
            job_soup = BeautifulSoup(str(element), "html.parser")

            # Extract job title
            title_tag = job_soup.find("a")

            if title_tag:
                job_titles.append(title_tag.text.strip())
            else:
                job_titles.append("-")

            # Extract company name
            company_tag = job_soup.find(
                "span",
                class_="listing-company-name"
            )

            if company_tag:
                company_lines = company_tag.get_text(
                    "\n", strip=True
                ).split("\n")

                cleaned = []

                for item in company_lines:
                    item = item.strip()

                    if item and item != "New":
                        cleaned.append(item)

                if len(cleaned) >= 2:
                    companies.append(cleaned[-1])
                else:
                    companies.append("-")
            else:
                companies.append("-")

            # Extract posted date
            posted_tag = job_soup.find("time")

            if posted_tag:
                posted_dates.append(posted_tag.text.strip())
            else:
                posted_dates.append("-")

            # Extract location
            location_tag = job_soup.find(
                "span",
                class_="listing-location"
            )

            if location_tag:
                locations.append(
                    location_tag.get_text(strip=True)
                )
            else:
                locations.append("-")

        except Exception as e:
            print("Error processing a job:", e)

            job_titles.append("-")
            companies.append("-")
            posted_dates.append("-")
            locations.append("-")

    # Step 6: Remove raw Info column
    job_df.drop("Info", inplace=True, axis=1)

    # Step 7: Create individual DataFrames
    title_df = pd.DataFrame(job_titles, columns=["Job Title"])
    company_df = pd.DataFrame(companies, columns=["Company"])
    posted_df = pd.DataFrame(posted_dates, columns=["Posted Date"])
    location_df = pd.DataFrame(locations, columns=["Location"])

    # Step 8: Combine DataFrames
    job_df = pd.concat(
        [title_df, company_df, posted_df, location_df],
        axis=1
    )

    job_df.columns = [
        "Job Title",
        "Company",
        "Posted Date",
        "Location"
    ]

    # Step 9: Save final job data
    output_file = (
        r"C:\Users\mani\OneDrive\Documents\Job_portal\job_posts.csv"
    )

    try:
        job_df.to_csv(output_file, index=False)

        print(job_df)
        print("job_df_Data_Stored_Successfully")

    except PermissionError as e:
        print("Permission denied while saving job_posts.csv.")
        print("Close the CSV file if it is open in Excel.")
        print("Error:", e)

    except Exception as e:
        print("Error saving job posts:", e)

except requests.exceptions.Timeout:
    print("Error: Website request timed out.")

except requests.exceptions.HTTPError as e:
    print("HTTP Error:", e)

except requests.exceptions.ConnectionError:
    print("Error: Unable to connect to the website.")

except requests.exceptions.RequestException as e:
    print("Request Error:", e)

except ValueError as e:
    print("Data extraction error:", e)

except PermissionError as e:
    print("File permission error:", e)

except Exception as e:
    print("Unexpected Error:", e)
