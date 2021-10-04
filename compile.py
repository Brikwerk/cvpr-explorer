import json
import time
import os
from urllib.parse import urljoin
import argparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('year', type=int,
                    help="""Specifies the CVPR year to compile into a library.""")
parser.add_argument('-d', '--delay', required=False, default=0.25,
                    help="""Specifies the delay between publications requests.""")
parser.add_argument('-u', '--useragent', required=False, default="CVPR-Explorer",
                    help="""Specifies the user-agent string for publication requests.""")
args = parser.parse_args()


def get_paged_papers(soup, base_url):

    all_papers = False
    page_links = []
    for page in soup.findAll('dd'):
        page_link = page.findAll("a")[0].get('href')
        if "all" in page_link:
            all_papers = page_link
            break
        else:
            page_links.append(page_link)
    
    if all_papers:
        url = urljoin(base_url, all_papers)
        html_text = requests.get(url).text
        page_soup = BeautifulSoup(html_text, 'html.parser')
        return page_soup.findAll('dt', {'class': 'ptitle'})
    else:
        paper_elms = []
        for page_link in page_links:
            url = urljoin(base_url, page_link)
            html_text = requests.get(url).text
            page_soup = BeautifulSoup(html_text, 'html.parser')
            paper_elms = paper_elms + page_soup.findAll('dt', {'class': 'ptitle'})
            time.sleep(args.delay)
        return paper_elms


if __name__ == "__main__":

    user_agent = "CVPR-Explorer"
    headers = {
        'User-Agent': user_agent
    }
    cvpr_base_url = "https://openaccess.thecvf.com"
    cvpr_year = args.year
    cvpr_url = f"{cvpr_base_url}/CVPR{cvpr_year}"

    html_text = requests.get(cvpr_url).text
    
    soup = BeautifulSoup(html_text, 'html.parser')

    print(f"Getting the publication list for CVPR {args.year}")
    if "Day 1: " in soup.select_one('dd').text:
        paper_elms = get_paged_papers(soup, cvpr_base_url)
    else:
        paper_elms = soup.findAll('dt', {'class': 'ptitle'})
    
    print(len(paper_elms), "publications found.")
    print("Compiling library...")

    papers = {}
    for i in tqdm(range(len(paper_elms))):
        paper_elm = paper_elms[i]
        try:
            paper_anchor = paper_elm.findAll('a')[0]
            paper_info_link = urljoin(cvpr_base_url, paper_anchor.get('href'))
            paper_title = paper_anchor.contents[0]

            html_text = requests.get(paper_info_link).text
            
            soup = BeautifulSoup(html_text, "html.parser")

            paper_abstract = soup.find('div', {'id': 'abstract'}).contents[0]
            paper_link = soup.findAll("a", string="pdf")[0].get('href')
            paper_link = urljoin(cvpr_base_url, paper_link)

            papers[i] = {
                "paper_title": paper_title,
                "paper_info_link": paper_info_link,
                "paper_link": paper_link,
                "paper_abstract": paper_abstract
            }

            time.sleep(args.delay)
        except Exception as e:
            print("\n\n--> ERROR <--")
            print(e)
            print("\n\n")
            time.sleep(args.delay)
    
    print("Writing library...")

    if not os.path.isdir("./libraries"):
        os.mkdir("./libraries")

    with open(f"./libraries/cvpr{cvpr_year}.json", "w") as f:
        f.write(json.dumps(papers, indent=4))

    print("Done!")
