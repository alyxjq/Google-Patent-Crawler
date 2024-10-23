import os
import time
import glob
import urllib.request
import pandas as pd
import random
#Randomly wait (WAITTING_TIME-1, WAITTING_TIME+1) seconds
WAITTING_TIME=2

folder_path = "patents"
failed_file_path = "logs/failed_file.csv"
output_path = "downloaded_pdfs"

def check_or_create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"The folder '{path}' does not exist, it has been successfully created!")
    else:
        print(f"The folder '{path}' already exists")

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
        print(f"Folder {folder_path} traversal exception")
        print(e)
    finally:
        return file_list_out

def save_failed_download_file(patentno, patent_pdf_url):
    df = pd.DataFrame({'Patent_number': [patentno], 'PDF_download_link': [patent_pdf_url]})
    df.to_csv(failed_file_path, mode='a', header=False, index=False)
    print(f"Save download failed files: {patent_pdf_url}")

if __name__ == '__main__':
    download_total = 0
    try:
        download_file_list = readPatentsPdfDownloadFile('patents')
        for download_file in download_file_list:
            output_path_new_folder  = output_path + "/" + download_file.split("\\")[-1].split(".")[0]
            check_or_create_folder(output_path_new_folder)
            df = pd.read_csv(download_file)
            print("Number of patent lines read: ",len(df))
            for index,row in df.iterrows():
                patentno       = row["Patent_number"]
                patent_pdf_url = row["PDF_download_link"]
                local_download_file_name = patent_pdf_url.split('/')[-1]
                local_download_file_name = f"{patentno}_{local_download_file_name}"
                print(f"Patent number: {patentno}, Local file name: {local_download_file_name}")
                local_path = f"{output_path_new_folder}/{local_download_file_name}"
                if not os.path.exists(local_path):
                    try:
                        response = urllib.request.urlopen(patent_pdf_url)
                        with open(local_path, "wb") as file:
                            file.write(response.read())
                        print(f"Patent: {patentno}, Download successful and save to local document: {local_path}")
                        download_total += 1
                        print(f"Successfully downloaded {download_total} patents!")
                    except Exception as e:
                        print("First download file exception Try again for the first time")
                        print(e)
                        try:
                            response = urllib.request.urlopen(patent_pdf_url)
                            with open(local_path, "wb") as file:
                                file.write(response.read())
                            print(f"Patent: {patentno}, Download successful and save to local document: {local_path}")
                            download_total += 1
                            print(f"Successfully downloaded {download_total} patents!")
                        except Exception as ex:
                            print("Attempted to download file abnormally, retry for the second time")
                            print(ex)
                            try:
                                response = urllib.request.urlopen(patent_pdf_url)
                                with open(local_path, "wb") as file:
                                    file.write(response.read())
                                print(f"Patent: {patentno}, Download successful and save to local document: {local_path}")
                                download_total += 1
                                print(f"Successfully downloaded {download_total} patents!")
                            except Exception as exx:
                                print("Failed to download document 3 times!")
                                save_failed_download_file(patentno, patent_pdf_url)
                                print(exx)
                    stime=random.uniform(WAITTING_TIME-1,WAITTING_TIME+1)
                    stime=round(stime,2)
                    print(f'Wait {stime} seconds to continue!')
                    time.sleep(stime)
                else:
                    time.sleep(0.1)
                    print('The file already exists, skip!')
    except Exception as e:
        print(e)
    finally:
        print("All documents have been downloaded!")
