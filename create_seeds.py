import calendar
import datetime
import pandas as pd
SAVE_FILE_NAME = "seeds.csv"
START_YEAR = "2001"
END_YEAR = "2001"
#Change to the international patent classification number you want
PATENT_NUMBER="H01L"
TODAY = datetime.date.today()
def create_seeds():
    df=pd.DataFrame(columns=["start_date","end_date","seed_url"])
    for year in range(int(START_YEAR), int(END_YEAR) + 1):
        for mon in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
            end_day = calendar.monthrange(year, int(mon))[1]
            if TODAY >= datetime.date(year, int(mon), end_day):
                seed_url=f"https://patents.google.com/?q=({PATENT_NUMBER})&before=priority:{str(year)}{mon}{end_day}&after=priority:{str(year)}{mon}01&language=CHINESE&num=100"
                df.loc[len(df)]=([f"{year}{mon}01",f"{year}{mon}{end_day}",seed_url])
                print(seed_url)
    df.to_csv(SAVE_FILE_NAME,index=False)
    
create_seeds()