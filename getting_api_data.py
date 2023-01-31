from fpdf import FPDF
import requests
import pandas as pd
import dataframe_image as dfi
import json

# Insert your API Key
API_KEY = 'Insert your NASA-API Key'
# Insert API URL
URL_APOD = "https://api.nasa.gov/planetary/apod"
# Additional parameters...
DATES = ['2022-12-{}'.format(day) for day in range(21, 10, -1)]


# Fetching data from API...
def fetch_api():
    responses = []
    # Iterate over additional parameters
    for date in DATES:
        # Parameters dictionary
        params = {
          'api_key': API_KEY,
          'date': date,
          'hd': 'True'
        }
        # Append contents from current url, to list of contents
        responses.append(requests.get(URL_APOD, params=params).json())

    # Adding contents to JSON file...
    with open('api_data.json', 'w') as outfile:
        json.dump(responses, outfile, indent=2)
        outfile.close()
    print(responses)


# Read contents from JSON file
with open('api_data.json') as infile:
    api_data = json.load(infile)
    infile.close()
# Create dataframe from contents
api_dataframe = pd.json_normalize(api_data)


class PDF(FPDF):
    def create_title(self, text):
        self.set_font('Helvetica', 'B', 20)
        self.write(5, text)
        self.ln(10)
        self.set_font('Helvetica', '', 8)

    def create_subtitle(self, text):
        self.set_font('Helvetica', '', 14)
        self.write(4, text)
        self.ln(10)
        self.set_font('Helvetica', '', 8)

    def create_table(self, dataframe):
        dfi.export(dataframe, "api_dataframe.png", table_conversion='matplotlib')
        self.image("api_dataframe.png", w=190)
        self.ln(10)


# Creating PDF file...
def create_pdf():
    pdf = PDF()

    # First page with Table of contents... #
    # Adding a page
    pdf.add_page()
    # Add a title
    pdf.create_title('Getting data from NASA API:')
    # Add a subtitle
    pdf.create_subtitle('Contents:')
    # Add table
    pdf.create_table(api_dataframe)

    for index, row in api_dataframe.iterrows():
        img_data = requests.get(row['hdurl']).content
        with open(f'images/{row["date"]}.png', 'wb') as image:
            image.write(img_data)
            image.close()

        # Adding a page
        pdf.add_page()
        # Add a title
        pdf.create_title('Date:' + row['date'])
        # Add a subtitle
        pdf.create_subtitle('Description:')
        pdf.write(3, row['explanation'])
        pdf.ln(10)
        pdf.image(f'images/{row["date"]}.png', w=190)
    pdf.output('report.pdf')


create_pdf()
