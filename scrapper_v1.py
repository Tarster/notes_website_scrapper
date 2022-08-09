import re
from bs4 import BeautifulSoup
import notes_html
import pandas as pd

html = notes_html.return_html()
HTML_PARSER_CONSTANT = 'html.parser'

def text_formatter(text):
    # Check if length is greater than 0
    if len(text) > 0:
        for index, char in enumerate(text):
            if char.isalpha() or char in ['""','?',"@","#","$","''"]:
                return text[index:]
        return ""
    else:
        return ""


# Remove the empty spaces from the html
html = re.sub(r'\s+',' ',html)
# replace the empty <p></p> tag in the html
html = re.sub(r'<p><\/p>',' ',html)
#remove the button part as well
html = re.sub(r'<button class.+?<\/button>',' ',html)
#2 more clean up patterns
html = re.sub(r'<p><br /></p>',' ',html)
# html = re.sub(r'<p>.+?<span.+?style.+?font.+?large.+?<\/span>.+?<\/p>',' ',html)
pattern = r'<p>.+?<ol.+?<\/ol>.+?<div.+?<\/p>\s*<\/div>'
# with open('test_html_1.txt', 'w') as f:
#     f.write(html)

# Create a new df and assign column names as well:
df = pd.DataFrame(columns=['Question','option1','option2','option3','option4','option5','option6','answer','last_checked_option'])

html_list = re.finditer(pattern, html)
for index, pattern_text in enumerate(html_list):
    dictionary = {'Question':"",
'option1':"",
'option2':"",
'option3':"",
'option4':"",
'option5':"",
'option6':"",
'answer':"",
'last_checked_option':""}
   
    # print(pattern_text.group(0))
    # find all the <p> tags before the <ol> tag in the each pattern
    p_tag_arrays = re.finditer(r'<p>.+?<ol', pattern_text.group(0))
    print(f'Question {index}:')
    final_question_string = ""
    for p_tag in p_tag_arrays:
        soup = BeautifulSoup(p_tag.group(0),features=HTML_PARSER_CONSTANT) 
        for i,para in enumerate(soup.find_all("p")):
            if i == 0:
                final_question_string = text_formatter(para.text)
            else:
                final_question_string += "\n{}".format(para.text)
    dictionary['Question'] = final_question_string
    print(final_question_string)

    li_tag_array =  re.findall(r'<ol.+?<\/ol>', pattern_text.group(0))
    print("Answer option:")
    soup = BeautifulSoup(li_tag_array[0],features=HTML_PARSER_CONSTANT)
    for index,li in enumerate(soup.find_all("li")):
        dictionary["option{}".format(index + 1)] = li.text
        print(text_formatter(li.text))
    # Lets find the actual answer now
    soup =  BeautifulSoup(pattern_text.group(0), features=HTML_PARSER_CONSTANT)
    answer_string = soup.find('div',class_= "mcq").find_all('p')[0].text
    # Remove the Answer and number part
    remove_answer_text = re.sub(r'A.+?.\)', '', answer_string)
    dictionary["answer"] = remove_answer_text
    #pushing the data in the frame
    df_dictionary = pd.DataFrame([dictionary])
    df = pd.concat([df, df_dictionary], ignore_index=True)
    # print(f"Answer:{remove_answer_text}") #.replace(' ','')
df = df.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
df.to_excel('test.xlsx',index=False)