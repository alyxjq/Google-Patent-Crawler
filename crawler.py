import os
import time
import glob
import asyncio
import pandas as pd
from pyppeteer import launch
from create_seeds import PATENT_NUMBER
#改成你自己的Chrome路径
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

print("chromium的启动路径为:",CHROME_PATH)

def getFirstUrlAndLoadExistData( folder ):
    firstUrl = ""
    datalists = []
    maxnum_file = ""
    file_pattern = os.path.join(folder, '**', '*')
    file_list = glob.glob(file_pattern, recursive=True)
    for file_path in file_list:
        if os.path.isfile(file_path):
            print(file_path)
            totalnumlist = file_path.split('_')
            totalstr = totalnumlist[-1]
            totalnumstr = totalstr[0:-4]
            totalnum = int(totalnumstr)
            if totalnum > maxnumber:
                maxnumber = totalnum
                maxnum_file = file_path
    if maxnumber == 0:
        firstUrl = f"https://patents.google.com/?q=({PATENT_NUMBER})&num=100&oq={PATENT_NUMBER}"     
    else:
        pagenum = int(maxnumber / 100)
        firstUrl = f"https://patents.google.com/?q=({PATENT_NUMBER})&num=100&oq={PATENT_NUMBER}&page={pagenum}"
        df = pd.read_csv(maxnum_file)
        for index, row in df.iterrows(): 
            patentno = row['专利号']
            downloadurl = row['PDF下载链接'] 
            datalists.append({"专利号":patentno,"PDF下载链接":downloadurl})
    return firstUrl,datalists

def saveLogs(url,page,logfile_path="logs/record.csv"):
    try:
        df_logs = pd.DataFrame(columns=['当前下载URL', '抓取页数'])
        if os.path.exists(logfile_path):
            df_logs = pd.read_csv(logfile_path)
        else:
            pass
        row_data = [url, str(page)]
        df_logs.loc[len(df_logs)] = row_data
        df_logs.to_csv(logfile_path,index=False)
    except Exception as e:
        print("记录日志异常")
        print(e)

def readlogsandurlseeds( seeds_url_file_path, logfile_path = "logs/record.csv" ):
    crawl_url    =   ""
    crawl_page   =   1
    seedcsv=pd.read_csv(seeds_url_file_path)
    start_date = seedcsv['start_date']
    end_date = seedcsv['end_date']
    seed_lines = seedcsv['seed_url']
    if  len(seed_lines) == 0:
        crawl_url = "",
        crawl_page = 0
        return crawl_url,crawl_page,start_date,end_date,seed_lines
    if os.path.exists(logfile_path):
        df_logs = pd.read_csv(logfile_path)
        crawl_url  = df_logs.loc[len(df_logs)-1]["当前下载URL"]
        crawl_page = df_logs.loc[len(df_logs)-1]["抓取页数"]
    else:
        crawl_url = seed_lines[0]
        crawl_page = 1
    return crawl_url,crawl_page,start_date,end_date,seed_lines

async def main():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    if not os.path.exists('patents'):
        os.makedirs('patents')
    firstUrl,crawl_page,sd,ed,seed_lines = readlogsandurlseeds("seeds.csv","logs/record.csv")
    print("获取到的下载链接: ")
    print(firstUrl)
    print("下载到的页数: ")
    print(crawl_page)
    print("按下回车键继续...")
    input("")
    browser = await launch(executablePath=CHROME_PATH,headless=False,args=['--disable-infobars','--window-size=1440,900'])
    page = await browser.newPage()
    await page.setViewport({'width':1440,'height':900})
    seed_index = 0
    for line in seed_lines:
        if line == firstUrl:
            break
        else:
            seed_index += 1
    total_retrieve_num = 0
    for i in range(len(seed_lines)):
        try:
            if i >= seed_index:
                crawl_url = seed_lines[i]
                to_date = ed[i]
                from_date = sd[i]
                await page.goto(crawl_url, {'timeout': 50000})
                craw_page_index = 0
                df = pd.DataFrame(columns=['专利号', 'PDF下载链接'])
                while craw_page_index < 10:
                    try:
                        time.sleep(3)
                        print("滚动到页面底部")
                        await page.evaluate('_ => {window.scrollBy(0, document.body.scrollHeight);}') 
                        await page.waitForNavigation()
                        craw_page_index += 1
                        print("获取pdfUrls...")
                        pdfUrls = await page.JJeval("a.pdfLink", '(nodes => nodes.map(n => n.href))')
                        i = 0
                        for pdfUrl in pdfUrls:
                            i += 1
                            total_retrieve_num += 1
                            patent_seq = pdfUrl.split('/')
                            patent_filename = patent_seq[-1]
                            print(patent_filename)
                            patent_no = patent_filename[0:-5]
                            print("专利号：" ,patent_no)
                            row_data = [patent_no,pdfUrl]
                            if len(patent_no) < 15:
                                df.loc[len(df)] = row_data
                                print("第",craw_page_index,"页，第",i,"个专利url为:",pdfUrl)
                    except Exception as ex:
                        print("获取专利下载链接失败！")
                        print(ex)
                    else:
                        print("成功获取了本页所有专利数据！")
                        df.to_csv(f"patents/patents_from_{from_date}_to_{to_date}.csv",index=False)
                        print("当前总计抓取到的专利数共计: ",total_retrieve_num)
                        saveLogs(crawl_url,craw_page_index,"logs/record.csv")
                    finally:
                        print("点击下一页")
                        await page.hover('paper-icon-button[icon="chevron-right"]')
                        await page.click('paper-icon-button[icon="chevron-right"]')
        except Exception as ex:
            print("下一个月！")
            print(ex)
    print("浏览器关闭")
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())
