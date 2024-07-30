import os
import threading
import time
# 初始化lancedb对象
import lancedb
import pyarrow as pa
import json
import traceback
from functools import wraps


class DBOperator:
    db = None
    tbl = None
    lock = threading.Lock()
    # 缓存刷到数据库的最大值
    cache_flush_threshold = 1000
    current_cache_size = 0
    data_cache_file_path = "/opt/lancedb_cache/lance_db.cache"
    data_cache_batch_no_path = "/opt/lancedb_cache/lance_db.cache.batch_no"

    # 防抖装饰器
    def debounce(func, wait=5):
        timer = None

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            nonlocal timer
            if timer:
                timer.cancel()
            if self.cache_flush_threshold <= self.current_cache_size:
                # 超过阈值，强制提交
                func(self, *args, **kwargs)
            else:
                # 定时任务延时提交
                timer = threading.Timer(wait, lambda: func(self, *args, **kwargs))
                timer.start()

        return wrapper

    def init_connection(self, url="/opt/lancedb_data/lancedb-yz"):
        self.db = lancedb.connect(url)
        schema = pa.schema([
            pa.field("vector", pa.list_(pa.float64(), list_size=512)),
            pa.field("file_id", pa.int32()),
            pa.field("phone_id", pa.string()),
            pa.field("app_code", pa.string()),
            pa.field("batch_no", pa.string()),
            pa.field("time", pa.int64())
        ])
        # 创建文件夹
        os.makedirs("/opt/lancedb_cache/", exist_ok = True)
        self.tbl = self.db.create_table("clip", schema=schema, exist_ok=True)
        # 将缓存全部入库（如果有的话）
        self.force_write(True)

    # 向db中添加数据，为提高吞吐量，先写入缓存文件，再从缓存文件读入内存，写入数据库
    def add_data(self, data):
        self.lock.acquire()
        try:
            # 构建 new json
            json_data = {
                "file_id": data["fileId"],
                "phone_id": data["phoneId"],
                "vector": data["vector"],
                "app_code": data["appCode"],
                "time": data["time"]
            }
            json_str = json.dumps(json_data)
            # write str to cache file
            with open(self.data_cache_file_path, 'a') as cache_file:
                # 使用write()方法逐行写入
                cache_file.write(json_str + '\n')
            self.current_cache_size = self.current_cache_size + 1
            self.write_cache_to_db()
        except Exception as e:
            print("写入缓存失败：" + str(e))
            traceback.print_exc()
        finally:
            self.lock.release()

    # 先更新本地缓存文件，剔除待删除数据，再删除数据库
    def delete_data(self, field, value):
        self.lock.acquire()
        try:
            print("开始删除数据：" + str(field) + " " + str(value))
            new_cache = []
            # read str from cache file
            if os.path.exists(self.data_cache_file_path):
                with open(self.data_cache_file_path, 'r') as cache_file:
                    # 使用write()方法逐行写入
                    line = cache_file.readline()
                    while line:
                        data = json.loads(line.strip())  # strip()去除行末的换行符
                        if data.get(field) != value:
                            new_cache.append(data)
                        line = cache_file.readline()
                # 写回原文件
                with open(self.data_cache_file_path, 'w') as cache_file:
                    # 使用write()方法逐行写入
                    for cache_data in new_cache:
                        cache_file.write(json.dumps(cache_data) + '\n')
            # 删除db中的文件
            self.tbl.delete(field + " = " + value)
            print("删除数据完成：" + str(field) + " " + str(value))
        except Exception as e:
            print("删除数据失败：" + str(e))
            traceback.print_exc()
        finally:
            self.lock.release()

    # 清理脏数据，先更新本地缓存文件，剔除待删除数据，再删除数据库
    def clean_dirty_data(self, more_then_file_id, phone_id):
        self.lock.acquire()
        try:
            print("开始清理数据：检材：" + str(phone_id) + " 文件起始位置：" + str(more_then_file_id))
            new_cache = []
            # read str from cache file
            if os.path.exists(self.data_cache_file_path):
                with open(self.data_cache_file_path, 'r') as cache_file:
                    # 使用write()方法逐行写入
                    line = cache_file.readline()
                    while line:
                        data = json.loads(line.strip())  # strip()去除行末的换行符
                        if data.get("phone_id") == phone_id and data.get("file_id") >= more_then_file_id:
                            new_cache.append(data)
                        line = cache_file.readline()
                # 写回原文件
                with open(self.data_cache_file_path, 'w') as cache_file:
                    # 使用write()方法逐行写入
                    for cache_data in new_cache:
                        cache_file.write(json.dumps(cache_data) + '\n')
            self.tbl.delete("phone_id = '" + str(phone_id) + "' and file_id >= " + str(more_then_file_id))
            print("清理数据完成：检材：" + str(phone_id) + " 文件起始位置：" + str(more_then_file_id))
        except Exception as e:
            print("清理数据失败：" + str(e))
            traceback.print_exc()
        finally:
            self.lock.release()

    @debounce
    def write_cache_to_db(self):
        print("commit " + str(self.current_cache_size))
        self.force_write(False)

    # 实际写入数据库函数
    def force_write(self, clean_old_data):
        batch_no = int(time.time() * 1000)
        # 从缓存中读取batch_no(若有，则表示上次的缓存文件还未提交完成，删除所有batch_no为xxx的数据，重新从缓存文件中读取)
        batch_no_cache_file_exist = os.path.exists(self.data_cache_batch_no_path)
        if batch_no_cache_file_exist:
            with open(self.data_cache_batch_no_path, 'r') as batch_no_cache_file:
                # 使用write()方法逐行写入
                batch_no = batch_no_cache_file.read()
        try:
            if clean_old_data and batch_no_cache_file_exist:
                self.tbl.delete("batch_no = '" + batch_no + "'")
            # record current batch_no to batch_no cache file
            with open(self.data_cache_batch_no_path, 'w') as batch_no_cache_file:
                batch_no_cache_file.write(str(batch_no))
            cache = []
            # read str from cache file
            if os.path.exists(self.data_cache_file_path):
                with open(self.data_cache_file_path, 'r') as cache_file:
                    line = cache_file.readline()
                    while line:
                        data = json.loads(line.strip())  # strip()去除行末的换行符
                        # 填充 batch_no 数据，方便批量删除
                        data["batch_no"] = batch_no
                        cache.append(data)
                        line = cache_file.readline()
            # 入库
            if len(cache) > 0:
                self.tbl.add(cache)
            # delete cache files
            if os.path.exists(self.data_cache_file_path):
                os.remove(self.data_cache_file_path)
            if os.path.exists(self.data_cache_batch_no_path):
                os.remove(self.data_cache_batch_no_path)
            self.current_cache_size = 0
        except Exception as e:
            print("更新缓存失败：" + str(e))
            traceback.print_exc()

    # 向量搜索 + sql过滤
    def search(self, vector, filter_sql, return_fields, limit_count=25):
        # return dict list
        q = self.tbl.search(vector).metric("cosine")
        if filter_sql and len(filter_sql) > 0:
            q = q.where(filter_sql, prefilter=True)
        if return_fields and len(return_fields) > 0:
            q = q.select(return_fields)
        return q.limit(limit_count).to_pandas().to_dict(orient='records')
