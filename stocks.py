import pandas as pd
import os
import datetime


def to_date(date_str):
    """문자열을 데이트 형대로 변환한다."""
    date_str = date_str.replace(" ", "")
    split = ""
    if date_str.find("-") > -1:
        split = "-"
    elif date_str.find(".") > -1:
        split = "."
    date_format = '%Y' + split + '%m' + split + '%d'
    try:
        result = datetime.datetime.strptime(date_str, date_format)
    except Exception as inst:
        print(date_str)
        print(inst)
        result = datetime.datetime.now()
    return result

class Stocks:
    """ 주식데이터  """

    #def __init__(self):
     #self.params = params

    def _get_naver_url(self, comp_code):
        """ 네이버 금융(http://finance.naver.com)에 넣어줌 """
        return 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=comp_code)

    def _get_stock_naver_data(self, comp_code, start_date):
        """네이버 매일 주식정보를 가져온다."""
        url = self._get_naver_url(comp_code)
        df = pd.DataFrame()

        # 네이버 웹 크롤링
        page = 1
        bf_date = ''
        while True:
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            page_data = pd.read_html(pg_url, header=0)[0]
            page_data = page_data.dropna()
            last_date = page_data.tail(1)['날짜'].to_string(index=False)
            if bf_date == last_date:
                break
            df = df.append(page_data, ignore_index=True)
            if start_date != '':
                if to_date(start_date) > to_date(last_date):
                    break
            if len(page_data) < 10:
                break
            page += 1
            bf_date = last_date

            # 필요 없는 날짜 제거
        if start_date != '':
            drop_cnt = 0
            df_len = len(df)
            for i in range(df_len):
                last_date = df.loc[df_len - i - 1, '날짜']
                if to_date(start_date) > to_date(last_date):
                    drop_cnt += 1
                else:
                    break
            if drop_cnt > 0:
                df = df[:-drop_cnt]

        # 정렬 및 컬럼명 변경
        if df.shape[0] != 0:
            df = df.sort_values(by='날짜')
            df.rename(columns={'날짜': 'date',
                               '종가': 'close',
                               '전일비': 'diff',
                               '시가': 'open',
                               '고가': 'high',
                               '저가': 'low',
                               '거래량': 'volume'}, inplace=True)
        return df

    def get_stock_data(self, comp_code):
       # comp_code = DataUtils.to_string_corp_code(comp_code)
        file_path = './data/chart_data/' + comp_code + '.csv'

        if os.path.isfile(file_path):
            stock_data = pd.read_csv(file_path)
            stock_data = stock_data[:-1]
            date_last = stock_data.tail(1)['date'].to_string(index=False)
            date_next = to_date(date_last) + datetime.timedelta(days=1)
            date_next = date_next.strftime("%Y-%m-%d")
            new_data = self._get_stock_naver_data(comp_code, date_next)
            if len(new_data) > 0:
                stock_data = stock_data.append(new_data, ignore_index=True)
                stock_data.to_csv(file_path, index=False)
        else:
            stock_data = self._get_stock_naver_data(comp_code, '')
            stock_data.to_csv(file_path, index=False)


        return stock_data


if __name__ == '__main__':
    Stocks().get_stock_data(comp_code="035720")
    #Stocks().get_stock_data(comp_code="035420")
    #Stocks().get_stock_data(comp_code="005930")
    #Stocks().get_stock_data(comp_code="000270")