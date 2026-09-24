import scrapy
import re
import os
import pandas as pd
from datetime import datetime
import boto3
from io import StringIO

inupt_files = os.getcwd() +f"\\Cemaco - {datetime.now().strftime('%d-%m-%Y')}\\"
if not os.path.isdir(inupt_files):
    os.mkdir(inupt_files)


def file_name_checker(name):
    for char in ['@','$','%','&','\\','/',':','*','?','"',"'",'<','>','|','~','`','#','^','+','=','{','}','[',']',';','!','-']:
        if char in name:
            name = name.replace(char, "__")
    return name

class CemaSpider(scrapy.Spider):
    name = "cema"
    custom_settings = {
        "CONCURRENT_REQUESTS": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
        # Optional: small delay to be polite / avoid blocks
        # "DOWNLOAD_DELAY": 0.5,
    }

    def __init__(self, input_file=None, output_file=None, *args, **kwargs):
            super(CemaSpider, self).__init__(*args, **kwargs)
            self.items = []
            self.start_time = datetime.now()
    
            # Handle input file name
            if input_file:
                # Strip .xlsx if user passed it, we'll add it ourselves
                base_name = input_file.replace('.xlsx', '').strip()
            else:
                raw = input('Enter input file name (e.g. Vidri_url): ')
                base_name = raw.replace('.xlsx', '').strip()
    
            self.input_file = base_name + '.xlsx'
    
            # Auto-generate output file name as "Output_<input_file_name>.xlsx"
            self.output_file = 'Output_' + base_name + '.xlsx'
    
            print(f"Input  file : {self.input_file}")
            print(f"Output file : {self.output_file}")
    
            # Create output directory if it doesn't exist
            if not os.path.isdir(inupt_files):
                os.makedirs(inupt_files, exist_ok=True)
    
    def start_requests(self):
        # file_name = input('Enter the file name')
        read_excel_content = pd.read_excel(self.input_file)
        read_excel_content = read_excel_content.fillna('')
        self.items = []
        for index,row in read_excel_content.iterrows():
            url = row['Product Url']
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9,en-IN;q=0.8',
                'cache-control': 'max-age=0',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
                'Cookie': 'VtexWorkspace=master%3Ac9054342-0bbe-4d9e-abfa-63ee1255fc98; _fbp=fb.1.1773225719847.92186558324354987.AQYCAQIB; vtex_binding_address=cemacogt.myvtex.com/; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjFjMGJkZGMxLWQ4YTAtNDk3NS04YTYwLWZkMmM4MmNlNDIzNSIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiIzZTFmNDRkMi0zZTYxLTQ2YmMtYjQ4My00OGJhNWIyOGI5M2YiLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6ImNlbWFjb2d0IiwiZXhwIjoxNzczNjU3NzM0LCJpYXQiOjE3NzMyMjU3MzQsImp0aSI6IjUzNDM0MWQ0LWI0ZWYtNGRjYy04MDMwLWNjM2U1NzM4OTY2YiIsImlzcyI6InNlc3Npb24vZGF0YS1zaWduZXIifQ.zHlxiB-gzQedD0mT1Q9h3y0iRR-qVMsoVK9O-RD-rkUVsbZSvcoEOxv1lnsajRMQaVl7yYaI6b6jTdkKkCKX1w; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkdUUSIsImN1cnJlbmN5U3ltYm9sIjoiUSIsImNvdW50cnlDb2RlIjoiR1RNIiwiY3VsdHVyZUluZm8iOiJlcy1HVCIsImNoYW5uZWxQcml2YWN5IjoicHVibGljIn0; VtexRCSessionIdv7=091d532a-b903-4d5c-861c-9901bd0b18f8; VtexRCMacIdv7=a9174f07-19c7-476a-97fe-300d89cc9430; ABTastySession=mrasn=&lp=https%253A%252F%252Fwww.cemaco.com%252Fchinchin-roll-around-abeja-skip-hop-907755%252Fp; CheckoutOrderFormOwnership=; checkout.vtex.com=__ofid=fccc8d19771b460da73fb5755996d4c3; _gcl_au=1.1.1562561223.1773225738; ABTasty=uid=6jq74kmpajqvk8eg&fst=1773225737424&pst=-1&cst=1773225737424&ns=1&pvt=1&pvis=1&th=1591596.1984736.1.1.1.1.1773225738361.1773225738361.0.1; scarab.visitor=%2266D609737A8B4F7D%22; scarab.profile=%22907755%7C1773225740%22; _hjSessionUser_483462=eyJpZCI6ImJlYzliNzg2LThjNzItNTRmZC04N2EzLWVhNThkMjU0NDI5MyIsImNyZWF0ZWQiOjE3NzMyMjU3NDYyMjUsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_483462=eyJpZCI6IjlkYTljOTdhLWFkZDAtNGY0My1iZWM1LThlNTdjMjJjYWRmMiIsImMiOjE3NzMyMjU3NDYyMjgsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _hjHasCachedUserAttributes=true; _ALGOLIA=anonymous-05e9c046-3af0-4371-b755-eff828b95ab7'
                }
            yield scrapy.Request(url,callback=self.parse, headers=headers)

    def parse(self, response):
        item = {}
        try:
            item['product_url'] = response.url
            # item['Title'] = response.xpath('//div[contains(@class,"productSkuName")]/text()').get('').strip()
            title = response.xpath('//h1[contains(@class,"productSkuName")]/text()').get('').strip()
            if title != '':
                item['Title'] = title
            else:
                item['Title'] = response.xpath('//div[contains(@class,"productSkuName")]/text()').get('').strip()
            sku = response.xpath('//meta[@property="product:sku"]/@content').get('').strip()
            item['sku'] = sku
            item['Image'] = response.xpath('//div[@class="absolute top-0 left-0 right-0 bottom-0"]//img//@src').get('').strip()
            strike_price = str(''.join([i.replace('Q','').strip() for i in response.xpath('//div[contains(@class,"pdpMainInfo")]//span[contains(text(),"Reg:")]//span//text()').getall()]))
            if strike_price != '':
                item['Offer Price (Q)'] = response.xpath('//meta[@property="product:price:amount"]/@content').get('').strip()
                item['Actual Price (Q)']= strike_price
            else:
                item['Actual Price (Q)']= response.xpath('//meta[@property="product:price:amount"]/@content').get('').strip()
            if item['Actual Price (Q)'] == '' and item['Offer Price (Q)'] == '':
                item['Actual Price (Q)'] = str(''.join([i.replace('Q','').strip() for i in response.xpath('//div[contains(@class, "productMain")]//span[contains(@class, "currencyContainer")]//span//text()').get('').strip()]))
            item['Brand'] = response.xpath('//meta[@property="product:brand"]/@content').get('').strip()
            item['taxonamy'] = ' | '.join(response.xpath('//div[@data-testid="breadcrumb"]//a//text()').getall())
            item['end_category'] = item['taxonamy'].split(' | ')[-1]
            self.items.append(item)
            # df = pd.DataFrame(self.items)
            # df.to_excel('cemaco_scraped_items.xlsx', index=False)
            yield item
        except Exception as e:
            with open('issue.txt','a') as f:
                f.write(str(response.url) +'\n')
        # for url_product in re.findall(r'<loc>([^>]*?)<\/loc>',response.text):
        #	 # url_product = url.xpath('./loc/text()').get('').strip()
        #	 # if 'https://www.kleintools.com/catalog' in url_product:  
        #	 item['url'] = url_product
        #	 yield item
        # breakpoint()
    def close(self, reason):
        # Convert the list of items into a DataFrame when the spider finishes
        
        df = pd.DataFrame(self.items)
        
        # Save the DataFrame to an Excel or CSV file
        df.to_excel(self.output_file, index=False)