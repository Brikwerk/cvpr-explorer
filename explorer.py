import os

import requests
import json
from rich import print
from rich.console import Console
import webbrowser
from tqdm import tqdm


def clear():

    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")


def strip(x):

    return x.strip()


def manually_filter(publications):

    console = Console()
    selected = {}
    count = 0
    for i, key in enumerate(publications.keys()):
        pub = publications[key]
        title = pub['paper_title']
        info_link = pub['paper_info_link']
        pdf_link = pub['paper_link']
        abstract = pub['paper_abstract']

        clear()

        print(f"[bold underline sky_blue2]{title}")
        console.print(f"[underline sky_blue3][{i}/{len(publications.keys())}]", end=" ")
        console.print("[underline sky_blue3][Info]", style=f"link {info_link}", end=" ")
        console.print("[underline sky_blue3][PDF]", style=f"link {pdf_link}")
        print("")

        print("[bold underline sky_blue3]Abstract")
        print(abstract)
        print("")

        print("[yellow]Would you like to select this publication?")
        print("[yellow](y/n) to accept/reject, (p) to view the PDF, (i) for more info.")
        response = input("> Response (y/n/p/i): ")

        while response == 'p' or response == 'i':
            if response == 'p':
                webbrowser.open(pdf_link)
            elif response == 'i':
                webbrowser.open(info_link)
            response = input("> Response (y/n/p/i): ")

        if response == 'y' or response == 'yes':
            selected[count] = pub
            count += 1
        
        if response == 'e':
            return selected
    
    return selected


def download(url, dest_folder):

    file_name = url.split("/")[-1]
    file_path = os.path.join(dest_folder, file_name)

    resp = requests.get(url, stream=True)

    if resp.ok:
        with open(file_path, 'wb') as f:
            for section in resp.iter_content(chunk_size=1024*8):
                if section:
                    f.write(section)
                    f.flush()
                    os.fsync(f.fileno())
    else:
        print(f"[bold red]Failed to download from {url}")
        print(f"[bold red]Details: {resp.status_code} {resp.text}")


if __name__ == "__main__":

    if not os.path.isdir("./libraries"):
        print("[bold red]Unable to detect the 'libraries' folder. Exiting...")
        exit(1)
    if len(os.listdir("./libraries")) < 1:
        print("[bold red]Unable to detect any CVPR libraries. Exiting...")
        exit(1)

    print(
        "[yellow]Please pick a folder name in which selected publications "
        "will be stored."
    )
    storage_folder = input("> Folder Name: ")
    while len(storage_folder) < 1:
        storage_folder = input("> Please enter a valid folder name: ")
    print("")

    print(
        "[yellow]Please enter keywords or phrases (separated by a comma) "
        "that you wish to filter publications by. \nPress enter if "
        "you do not wish to filter any publications."
    )
    pub_filters = input("> Filter: ")
    print("")
    if pub_filters == '':
        pub_filters = None
    else:
        pub_filters = list(map(strip, pub_filters.split(",")))

    print(
        "[yellow]Please select the CVPR libraries you wish to search. "
        "To select a library, type the number beside it. \nTo select "
        "multiple libraries, separate the numbers with commas."
    )
    libraries = os.listdir("./libraries")
    libraries.sort()
    for i, library in enumerate(libraries):
        print(f"[bold blue][{i}] {library}")

    selected_library_nums = input("> Selected: ")
    selected_library_nums = list(map(strip, selected_library_nums.split(",")))
    print("")

    if len(selected_library_nums) > 1:
        print("[yellow]Loading libraries...")
    else:
        print("[yellow]Loading library...")

    selected_libraries = []
    for i in selected_library_nums:
        if not i.isdigit():
            print("[bold red]Library selection is not a number. Exiting...")
            exit(1)
        i = int(i)

        with open(os.path.join("./libraries", libraries[i])) as f:
            selected_libraries.append(json.load(f))
    
    publications = {}
    if pub_filters is not None:
        if len(selected_library_nums) > 1:
            print("[yellow]Filtering libraries...")
        else:
            print("[yellow]Filtering library...")
        
        count = 0
        # Loop over all libraries
        for library in selected_libraries:
            # Loop through each publication in the library
            for key in library.keys():
                publication = library[key]
                # Filter by publication filters specified
                for pub_filter in pub_filters:
                    # Find case insensitive matches in the paper title or abstract
                    if (pub_filter.lower() in publication['paper_title'].lower()
                            or pub_filter.lower() in publication['paper_abstract'].lower()):
                        publications[count] = publication
                        count += 1
    else:
        if len(selected_library_nums) > 1:
            print("Compiling libraries...")
        else:
            print("Compiling library...")
        count = 0
        for library in selected_libraries:
            for key in library.keys():
                publications[count] = library[key]
                count += 1
    print("")
    
    if len(publications.keys()) < 1:
        print("[bold red]No publications found. Exiting...")
        exit(0)
    
    print(
        "[yellow]Would you like to manually filter the selected "
        "publications? \nIf not, all publication PDFs will be downloaded "
        "from the list."
    )
    manual_filtering = input("> Response (y/n): ")
    print("")

    if manual_filtering == 'y' or manual_filtering == 'yes':
        publications = manually_filter(publications)
    
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)
    
    json_path = os.path.join(storage_folder, 'publications.json')
    with open(json_path, 'w') as f:
        json.dump(publications, f, indent=4)
    
    print("")

    print("[yellow]Downloading PDFs...")
    publication_keys = list(publications.keys())
    for i in tqdm(range(len(publication_keys))):
        pub = publications[publication_keys[i]]
        download(pub['paper_link'], storage_folder)
    print("")
    
    print("[bold green]Done!")
