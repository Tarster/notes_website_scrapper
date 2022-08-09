# This file is made to scrape the www.notesbureau.com.

import os
import time
import sys
import re
import pandas as pd
import xlsxwriter
# Selenium Imports
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Other Imports
from bs4 import BeautifulSoup
paths = [r'C:\TCS\Fresco_Automation\General_Classes', r'C:\TCS\Fresco_Automation\Fresco_Phase_2\notes.txt']
for path in paths:
    sys.path.append(path)
import Common_Functions as CF

HTML_PARSER_CONSTANT = 'html.parser'


class Scrape_1(object):
    '''
    Scrapping Notes bureau using this class
    '''

    def __init__(self):
        # Below 2 lines will keep my browser window open upon completion of the script
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Entering the username into the username field
        # This will create a instance of my browser
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.common_instance = CF.CommonFunctions()

    # This will cleanup the data
    def data_cleaner(self, html: str) -> str:
        # Remove the empty spaces from the html
        html = re.sub(r'\s+', ' ', html)
        # replace the empty <p></p> tag in the html
        html = re.sub(r'<p><\/p>', ' ', html)
        # remove the button part as well
        html = re.sub(r'<button class.+?<\/button>', ' ', html)
        # 1 more clean up patterns
        html = re.sub(r'<p><br /></p>', ' ', html)
        # Finally return the cleaned up HTML
        return html

    def course_complete_extractor(self, html_list):

        # Create a new df and assign column names as well:
        df = pd.DataFrame(columns=['Question','option1','option2','option3','option4','option5','option6','answer','last_checked_option'])

        for index, pattern_text in enumerate(html_list):
            dictionary = {'Question': "",
                          'option1': "",
                          'option2': "",
                          'option3': "",
                          'option4': "",
                          'option5': "",
                          'option6': "",
                          'answer': "",
                          'last_checked_option': ""}

            # find all the <p> tags before the <ol> tag in the each pattern
            p_tag_arrays = re.finditer(r'<p>.+?<ol', pattern_text.group(0))
            print(f'Question {index}:')
            final_question_string = ""
            for p_tag in p_tag_arrays:
                soup = BeautifulSoup(p_tag.group(0), features=HTML_PARSER_CONSTANT)
                for i, para in enumerate(soup.find_all("p")):
                    if i == 0:
                        final_question_string = self.text_formatter(para.text)
                    else:
                        final_question_string += "\n{}".format(para.text)
            # Question string extracted successfully 
            dictionary['Question'] = final_question_string

            # Working on answer options
            li_tag_array = re.findall(r'<ol.+?<\/ol>', pattern_text.group(0))
            soup = BeautifulSoup(li_tag_array[0], features=HTML_PARSER_CONSTANT)
            for index, li in enumerate(soup.find_all("li")):
                dictionary["option{}".format(index + 1)] = li.text
                
            # Lets find the actual answer now
            soup = BeautifulSoup(pattern_text.group(0), features=HTML_PARSER_CONSTANT)
            answer_string = soup.find('div', class_="mcq").find_all('p')[0].text
            # Remove the Answer and number part
            remove_answer_text = re.sub(r'A.+?.\)', '', answer_string)
            dictionary["answer"] = remove_answer_text
            # pushing the data in the frame
            df_dictionary = pd.DataFrame([dictionary])
            df = pd.concat([df, df_dictionary], ignore_index=True)
            # print(f"Answer:{remove_answer_text}") #.replace(' ','')
        df = df.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
        return df

    def text_formatter(self, text: str) -> str:
        # Check if length is greater than 0
        if len(text) > 0:
            for index, char in enumerate(text):
                if char.isalpha() or char in ['""', '?', "@", "#", "$", "''"]:
                    return text[index:]
            return ""
        else:
            return ""

    def scrape_caller(self):
        # Opening the file which contain all the links
        lines = []
        with open(r'C:\TCS\Fresco_Automation\Fresco_Phase_2\notes.txt') as f:
            lines = f.readlines()

        # Visiting the link in the list
        for mcq in lines:
            mcq = mcq.replace("\n", "").split(',')[0]
            excel_file_name = mcq.split("/")[-1].split(".")[0]
            excel_file_name = r"C:\TCS\Fresco_Automation\Excel_Files\{}.xlsx".format(excel_file_name)
            # print(excel_file_name)
            # Visiting the first link
            print(mcq)
            self.driver.get(mcq)
    
            #getting the html code
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="post-body"]')))
            html_content = element.get_attribute('innerHTML')
            div = self.data_cleaner(html_content)
            pattern = r'<p>.+?<ol style.+?<\/ol>.+?<div class="mcq".+?<\/p>'
            html_list = re.finditer(pattern, div)    
            df = self.course_complete_extractor(html_list)
            
            writer = pd.ExcelWriter(excel_file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            workbook=writer.book
            worksheet = writer.sheets['Sheet1']
            format = workbook.add_format({'text_wrap': True})
            for index in range(0,9):  
                # print(index)
                # Setting the format but not setting the column width.
                if index == 0:
                    column_width = 80
                else:
                    column_width = 30

                worksheet.set_column(index,index,column_width, format)
            writer.save()
            time.sleep(6)
        self.driver.quit()
            
scrape = Scrape_1()
scrape.scrape_caller()
