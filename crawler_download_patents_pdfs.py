import os
import time
import glob
import urllib.request
import pandas as pd
import random
#随机等待(WT-1,WT+1)秒
WAITTING_TIME=2
folder_path = "patents"
file_name   = "patents_info_1000.csv"
failed_file_path = "logs/failed_file.csv"
output_path = "downloaded_pdfs"

def check_or_create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"文件夹'{path}'不存在，已经创建成功！")
    else:
        print(f"文件夹'{path}'已经存在")

def readPatentsPdfDownloadFile(folder_path):
    file_list_out = []
    try:
        file_pattern = os.path.join(folder_path, '**', '*')
        file_list = glob.glob(file_pattern, recursive=True)
        for file_path in file_list:
            if os.path.isfile(file_path):
                if "patents_from_" in file_path:
                    print(file_path)
                    file_list_out.append(file_path)
    except Exception as e:
        print(f"文件夹{folder_path}遍历异常")
        print(e)
    finally:
        return file_list_out

def save_failed_download_file(patentno, patent_pdf_url):
    df = pd.DataFrame({'专利号': [patentno], 'PDF下载链接': [patent_pdf_url]})
    df.to_csv(failed_file_path, mode='a', header=False, index=False)
    print(f"保存失败文件：{patent_pdf_url}")

if __name__ == '__main__':
    download_total = 0
    try:
        download_file_list = readPatentsPdfDownloadFile('patents')
        for download_file in download_file_list:
            output_path_new_folder  = output_path + "/" + download_file.split("\\")[-1].split(".")[0]
            check_or_create_folder(output_path_new_folder)
            df = pd.read_csv(download_file)
            print("读取到的专利行数: ",len(df))
            for index,row in df.iterrows():
                patentno       = row["专利号"]
                patent_pdf_url = row["PDF下载链接"]
                local_download_file_name = patent_pdf_url.split('/')[-1]
                local_download_file_name = f"{patentno}_{local_download_file_name}"
                print(f"专利号：{patentno},本地文件名称：{local_download_file_name}")
                local_path = f"{output_path_new_folder}/{local_download_file_name}"
                if not os.path.exists(local_path):
                    try:
                        response = urllib.request.urlopen(patent_pdf_url)
                        with open(local_path, "wb") as file:
                            file.write(response.read())
                        print(f"专利: {patentno} 下载成功，并存入本地文档: {local_path}")
                        download_total += 1
                        print(f"成功下载了{download_total}篇专利！")
                    except Exception as e:
                        print("首次下载文件异常 ... 重试第1次")
                        print(e)
                        try:
                            response = urllib.request.urlopen(patent_pdf_url)
                            with open(local_path, "wb") as file:
                                file.write(response.read())
                            print(f"专利: {patentno} 下载成功，并存入本地文档: {local_path}")
                            download_total += 1
                            print(f"成功下载了{download_total}篇专利！")
                        except Exception as ex:
                            print("重试下载文件异常，重试第2次")
                            print(ex)
                            try:
                                response = urllib.request.urlopen(patent_pdf_url)
                                with open(local_path, "wb") as file:
                                    file.write(response.read())
                                print(f"专利: {patentno} 下载成功，并存入本地文档: {local_path}")
                                download_total += 1
                                print(f"成功下载了{download_total}篇专利！")
                            except Exception as exx:
                                print("下载文档3次失败！")
                                save_failed_download_file(patentno, patent_pdf_url)
                                print(exx)
                    stime=random.uniform(WAITTING_TIME-1,WAITTING_TIME+1)
                    stime=round(stime,2)
                    print(f'等待{stime}秒继续！')
                    time.sleep(stime)
                else:
                    time.sleep(0.1)
                    print('文件已经存在，跳过！')
    except Exception as e:
        print(e)
    finally:
        print("全部文档下载完毕！")
