from fastapi import FastAPI
import numpy as np
import lancedb
import json
import traceback
from ClipIndexRequest import ClipIndexRequest
from ClipSearchRequest import ClipSearchRequest
from LanceDBDeleteRequest import LanceDBDeleteRequest
from LanceDBCleanRequest import LanceDBCleanRequest
from DBOperator import DBOperator
from starlette.responses import PlainTextResponse

# 初始化db操作库
dbOperator = DBOperator()
dbOperator.init_connection()
# 初始化fastapi，对外提供http服务
app = FastAPI()


@app.post("/vectorDB/add", response_class=PlainTextResponse)
def insert_db(request: ClipIndexRequest):
    try:
        dbOperator.add_data(request.dict())
        return "success"
    except Exception as e:
        traceback.print_exc()
        return "error"
		
		
@app.post("/vectorDB/search")
def search_db(request: ClipSearchRequest):
    try:
        sub_sqls = []
        if request.phoneIds:
            # 构建phone_id查询语句
            sub_sqls.append("(phone_id IN (" + ", ".join([f"'{str(element)}'" for element in request.phoneIds]) + "))")
        if request.appCodes:
            # 构建appCode查询语句
            sub_sqls.append("(app_code IN (" + ", ".join([f"'{str(element)}'" for element in request.appCodes]) + "))")
        if request.startTime and request.endTime:
            # 构建时间查询语句，时间由调用方上层逻辑转成long格式对比
            sub_sqls.append("(time >= " + str(request.startTime) + " AND time <= " + str(request.endTime) + ")")
        sql = " AND ".join(sub_sqls)
        # 返回查询结果
        raw_list = dbOperator.search(request.vector, sql, ["file_id", "phone_id", "batch_no", "app_code", "time"], request.maxNum)
        new_list = []
        for it in raw_list:
            # print(type(it["vector"]))
            new_it = {
                "fileId": it["file_id"],
                "appCode": it["app_code"],
                "phoneId": it["phone_id"],
                "time": it["time"]
            }
            new_list.append(new_it)
        data = {
            "images": new_list
        }
        # print(str(data))
        return data
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        return {}


@app.post("/vectorDB/delete")
def delete_data_from_db(request: LanceDBDeleteRequest):
    try:
        dbOperator.delete_data(request.key, request.value)
        return "success"
    except Exception as e:
        traceback.print_exc()
        return "error"
        

@app.post("/vectorDB/clean")
def clean_data_from_db(request: LanceDBCleanRequest):
    try:
        dbOperator.clean_dirty_data(request.moreThenFileId, request.phoneId)
        return "success"
    except Exception as e:
        traceback.print_exc()
        return "error"
    
