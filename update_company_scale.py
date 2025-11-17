import sqlalchemy
import pandas as pd
from utils import get_company_base_info, update_loc_method
from FOF99Api import FOF99Api
from config import SQL_PASSWORDS, SQL_HOST

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/Euclid?charset=utf8"
)

# 读取所有数据
comp_code_list = pd.read_sql_query(
    "SELECT DISTINCT comp_code FROM fund_basic_info WHERE LENGTH(comp_code) = 8", engine
)
data = pd.read_sql_query("SELECT * FROM Euclid.company_scale", engine)
# 打印并未收录在 company scale 中的管理人
print(comp_code_list[~comp_code_list["comp_code"].isin(data["comp_code"].to_list())])
fof_99 = FOF99Api()

for i, row in data.iterrows():
    # 依据登记编号从火富牛中获取管理人信息
    registerNo = row["comp_code"]
    company_info = fof_99.get_company_info(registerNo)[0]
    for data_name, var in {
        "fund_num": "运作中产品数",
        "scale": "管理规模",
        "name_short": "管理人名称",
    }.items():
        update_loc_method(
            engine=engine,
            table_name="company_scale",
            key="comp_code",
            var=var,
            data={row["comp_code"]: company_info[data_name]},
        )
    print(f"已更新第{i + 1}条数据: {company_info[data_name]}")
