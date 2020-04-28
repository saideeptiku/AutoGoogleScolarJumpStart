import refextract
import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep


def get_refs(file_path):
    """list of references in pdf file"""
    print("File:", file_path)
    refs = refextract.extract_references_from_file(str(file_path))

    # iterate over refs
    for i, ref in enumerate(refs):

        # skip this if this is a link
        if "http" in "".join(ref['raw_ref']):
            continue

        # get title of this work
        title = ref.get('title', None)

        # if not none pass on
        # if title was read
        if title is not None:
            title = " ".join(title).lower()
            yield title


def get_files(folder):
    """get all files under folder"""

    # iter over each file
    for f in os.listdir(folder):

        # check if this is a pdf
        if f.split(".")[-1] == "pdf":
            yield folder + "/" + f


def write_titles(out_file, indir="files/"):
    """write titles to a local file"""

    titles = []

    # get this file
    for fp in get_files("files"):

        # get title
        for title in get_refs(fp):

            titles.append(title)

    print(f"found {len(set(titles))} titles.")

    with open(out_file, 'w') as f:
        for t in titles:
            f.write(f"{t}\n")

    return titles


def read_titles(out_file, indir="files/"):
    """read titles from a local file"""
    with open(out_file, 'r') as f:
        lines = f.readlines()

    for i, l in enumerate(lines):
        lines[i] = l.strip()

    return lines


def init_driver():
    """init webdriver"""
    return webdriver.Firefox()


def login_gs(driver):
    """login to google scholar"""
    login_link = "https://accounts.google.com/signin/v2/identifier?hl=en&continue=https%3A%2F%2Fscholar.google.com%2F&flowName=GlifWebSignIn&flowEntry=ServiceLogin"

    driver.get(login_link)

    input("Login to scholarly and hit any key here...")

    return driver


def check_robot(driver):
    """check if gs is asking for captcha confirmation"""
    print("checking robot")
    try:
        driver.find_element_by_id("gs_captcha_ccl")
    except:
        return False

    input("Robot Checkpoint. Press any key when done...")
    return True


def check_is_saved(driver):
    """check if the first publication is saved in library using css"""
    svg = driver.find_element_by_class_name("gs_or_svg")
    fill = svg.value_of_css_property("fill")

    if fill == 'none':
        return False

    return True


def search_gs(pub_search_txt, driver):
    start_page = "https://scholar.google.com/"
    input_xpath = '//input[@id="gs_hdr_tsi"]'

    # go to main search page
    driver.get(start_page)

    sleep(2)
    check_robot(driver)

    # go to start page
    elem = driver.find_element_by_xpath(input_xpath)

    elem.send_keys(pub_search_txt)

    elem.send_keys(webdriver.common.keys.Keys.ENTER)

    return driver


def feeling_lucky_gs_save(pub_search_txt, driver):
    """save the first publication result to user library"""
    search_gs(pub_search_txt, driver)

    sleep(1)

    # go to start page
    check_robot(driver)
    save_button = driver.find_element_by_class_name("gs_or_sav")

    # check if already saved
    if check_is_saved(driver):
        print("Already saved. Skipping...")
        return

    save_button.click()

    sleep(3)


def process_titles(titles, driver):
    """lookup each publication title in list using driver"""
    # work each title
    for i, pub_title in enumerate(titles):

        if i % 30 == 0 and i != 0:
            print("made many requests. wait for 30s cool down...")
            sleep(30)

        print(f"[{i + 1}]\t{pub_title}")
        feeling_lucky_gs_save(pub_title, driver)
        print("\n\n")


if __name__ == "__main__":

    # read all the titles
    titles = read_titles("files.txt")

    titles = list(set(titles))

    driver = init_driver()

    driver = login_gs(driver)

    process_titles(titles, driver)
