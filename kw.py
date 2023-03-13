import inflect
import openai
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")



openaikey = st.text_input('Enter your Open AI API Key (required)', '')


@st.cache_data
def getKey(openaikey):
    return openaikey
getKey(openaikey)

outputKw = st.checkbox('Use AI to give me a list of keywords for each product')
outputTitles = st.checkbox('Use AI to give me an optimised title for each product')


kw_prompt_text="imagine you're an amazon uk seller optimisation expert and write me a comma separated list of 30 single-word keywords that will help this product sell more - use British spellings: "
title_prompt_text= "Write an amazon product title for a piece of jewellery. Incorporate keywords such as the metal type (e.g. Sterling Silver, 9ct Gold, as well as related terms like 925 for silver), gemstone type (only if a stone is mentioned), the gender of the intended recipient, any unique design features, the occaision where the item might be gifted (e.g. birthday, anniversary), use words like quality, authentic, real. Cram the title with keywords. Use British spellings: "




def cleanKw(kw, product_name):
    keyword_list = kw.split()
    product_name_list = product_name.split()

    # Remove any words that match the product_name, including singular and plural forms
    p = inflect.engine()
    cleaned_keyword_list = []
    for word in keyword_list:
        if word in product_name_list:
            continue
        plural = p.plural(word)
        singular = p.singular_noun(word) or word
        if plural in product_name_list or singular in product_name_list:
            continue
        cleaned_keyword_list.append(word)

    # Remove any repeated words from the cleaned_keyword_list
    cleaned_keyword_list = list(set(cleaned_keyword_list))

    cleaned_keywords = " ".join(cleaned_keyword_list)

    return cleaned_keywords


def prompt(product_name, prompt_text, openaikey):
    if openaikey and (outputKw or outputTitles):
        try:
            # create a completion
            prompt = prompt_text + product_name
            openai.api_key = openaikey
            #st.write(prompt)
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
            #ƒstst.write(completion)
            # return only the text itself:
            kw = completion["choices"][0].message.content;

            if outputKw:
                # replace the commas with spaces for correct format for Amazon:
                kw = kw.replace(',', ' ')
                kw = cleanKw(kw, product_name)
                return kw

            else:
                return kw

        except Exception as e:
            st.warning("An error occurred while calling the OpenAI API: {}".format(str(e)))
            return ""


        return kw
    else:
        st.warning("you're missing something")
        return ""



# Define a function to load the CSV file
def load_data(file):
    data = pd.read_csv(file)
    if outputKw:
        data["keywords"] = data.apply(lambda row: prompt(row["product_name"], kw_prompt_text, openaikey).strip(), axis=1)
        return data
    else:
        data["title"] = data.apply(lambda row: prompt(row["product_name"], title_prompt_text, openaikey).strip(), axis=1)
        return data

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')



# Define the main function to display the app
def main():
    # Set up the app title
    st.title("The Amazing AI Amazon Keyword-ifier")
    # Prompt the user to select a CSV file
    file = st.file_uploader("Upload a CSV file", type="csv")
    st.write('file must be of format: asin, sku, product_name')

    # If the user has selected a file, load it into a data frame
    if file is not None:
        df = load_data(file)
        # Display the data frame in Streamlit
        st.write(df)
        csv = convert_df(df)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='amazon-kw.csv',
            mime='text/csv',
        )





# Call the main function to run the app
if __name__ == "__main__":
    main()










# print the completion
#output = (completion.choices[0].text)
#st.write(output)
#st.write(len(output))



# import a csv of: sku, asin, product name

#using the prompt for each product, save the space-separated list in a dataframe

#export that as csv