from typing import Any
import pandas as pd
from django.core.management.base import BaseCommand
from store.models import Product, Rating
from sqlalchemy import create_engine    

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        # csv_file = 'data_products/crawled_data_the_thao_da_ngoai.csv'

        csv_file = 'data_comments_all_fixed.csv'

        # dien_thoai_may_tinh_bang
        # do_choi_me_be
        # dien_gia_dung
        # nha_cua_doi_song
        # thoi_trang_nu
        # thiet_bi_kts_phu_kien_so
        # o_to_xe_may_xe_dap
        # lam_dep_suc_khoe 
        # bach_hoa_online 
        # the_thao_da_ngoai 
        df = pd.read_csv(csv_file)

        #xóa đi data không có description
        # length = df['short_description'].apply(len)
        # df = df.drop(df[length < 10].index)
        
        # #sửa lại price và sale_price về float
        # df['price'] = df['price'].astype(float).round(2)
        

        # df = df.drop(columns=['sku'])
        # df = df.drop(columns=['product_link'])
        # df = df.drop(columns=['list_price'])
        # df = df.drop(columns=['price_usd'])
        # df = df.drop(columns=['discount'])
        # df = df.drop(columns=['discount_rate'])
        # df = df.drop(columns=['review_count'])
        # df = df.drop(columns=['order_count'])
        # df = df.drop(columns=['inventory_status'])
        # df = df.drop(columns=['is_visible'])
        # df = df.drop(columns=['stock_item_qty'])
        # df = df.drop(columns=['stock_item_max_sale_qty'])
        # df = df.drop(columns=['product_name'])
        

        # df['category_id'] = 10

        # #Đổi tên 
        # df.rename(columns={'id': 'tiki_product_id'}, inplace=True)
        # df.rename(columns={'short_description':'description'}, inplace=True)
        # df = df.drop_duplicates()
        
        # df.reset_index(drop=True, inplace=True)
        # print(df)
        # # duplicate_ids = df[df.duplicated(subset=['tiki_product_id'], keep=False)]
        # # print(duplicate_ids['tiki_product_id'])
        
        # #Dành cho comment

        # df = df.drop(columns=['thank_count'])
        # df = df.drop(columns=['created_at'])
        # df = df.drop(columns=['purchased_at'])

        # rows_with_null_customer_name = df[df['customer_name'].isnull()]
        # df = df.drop(rows_with_null_customer_name.index, axis=0)

        # df.reset_index(drop=True, inplace=True)

        

        print(df)



        #Dành cho chung

        engine = create_engine('sqlite:///db.sqlite3')
        df.to_sql(Rating._meta.db_table, if_exists='append', con=engine, index=False)
        