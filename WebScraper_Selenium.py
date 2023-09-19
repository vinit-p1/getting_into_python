from string import printable
from selenium import webdriver
from selenium.webdriver.common.by import By
import aiohttp
import asyncio
import re
import time

async def download_photo(session, url):
    async with session.get(url) as response:
        filename = re.sub('[^0-9a-zA-Z]+', '', url.split("/")[-1]) + ".jpg"
        with open(filename, "wb") as f:
            async for data in response.content.iter_chunked(1024):
                f.write(data)

async def main():
    driver = webdriver.Chrome()
    driver.get('https://www.pap.pl/')

    cookies = driver.find_element(by=By.XPATH, value='//*[@id="cookie"]/div/div/div/div/div/div[1]')
    cookies.click()
    time.sleep(2)

    driver.maximize_window() 
    time.sleep(2)

    language_button= driver.find_element(by=By.XPATH, value='//*[@id="navbar"]/ul[2]/li[3]/a')
    language_button.click()
    time.sleep(2)

    business_button = driver.find_element(by=By.XPATH, value='//*[@id="block-mainnavigationen"]/ul/li[3]/a')
    business_button.click()
    time.sleep(2)

    titles = []
    while True:
        # Get all titles on current page
        title_group= driver.find_element(by=By.XPATH,value="/html/body/div/div[2]/section[2]/div/div[2]/div[1]/div[2]")
        titles_on_page = title_group.find_elements(by=By.CLASS_NAME, value='title')
        for title in titles_on_page:
            titles.append(title.text)

        with open('extracted_titles.txt', 'w') as f:
            for title in titles:
                f.write(title + '\n')
            

        photo_elements = title_group.find_elements(by=By.XPATH,value=".//img")
        photo_urls = [photo.get_attribute("src") for photo in photo_elements]

        # Downloading the photos to the current directory using aiohttp
        async with aiohttp.ClientSession() as session:
            tasks = [download_photo(session, url) for url in photo_urls]
            await asyncio.gather(*tasks)

        
        # Scroll down the page
        driver.execute_script("window.scrollBy(0,1200)","")
        time.sleep(2)


        last_page_button = driver.find_element(by=By.XPATH, value="/html/body/div/div[2]/section[2]/div/div[2]/div[1]/div[2]/div/nav/ul/li[6]/a")
        time.sleep(2)
        last_page_button.click()
        last_page_number= driver.find_element(by=By.XPATH, value="/html/body/div/div[2]/section[2]/div/div[2]/div[1]/div[2]/div/nav/ul/li[6]/a")
        print(f"Last page number: {last_page_number.text}")
            
        break
    driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
