import json
import threading
from locust import HttpUser, between, task, constant
import random

f = open('postFile.json', 'r')
fileJson = json.load(f)

def genHeaders(userId):
    return {'content-type': 'application/json',
            'x-app-key': 'user' + str(userId)}

def genDetail():
    return "お世話になっております。\n 負荷試験のため、データを登録させていただきます。\n\nよろしくお願いいたします。"

def getAccessUserId():
    return random.randint(1, 10000)

def getRecordId():
    return random.randint(1, 100000)

newFileId = []
newRecordId = []
newItemInfo = []
newItemForThumbInfo = []

def getNewFileInfo():
    tlock = threading.Lock()
    with tlock:
        try:
            if len(newFileId) != 0:
                return newFileId.pop()
        except:
            pass
    fid = random.randint(1, 1000)
    return {"fileId": "file_" + str(fid), "thumbFileId": "thumb_" + str(fid)}

class WebAppTestTasks(HttpUser):
    wait_time = constant(0.9)
    #@task
    def index(self):
        self.client.get("/api/hello", timeout=50)
    @task
    def getRecords(self):
        new = False
        recordId = getRecordId()
        userId = getAccessUserId()

        tlock = threading.Lock()
        with tlock:
            try:
                if len(newRecordId) != 0:
                    recordId = newRecordId.pop()
                    new = True
            except:
                pass
        r = self.client.get(url= "/api/client/records/" + str(recordId),
                        headers= genHeaders(userId), name="/records/[recordId]", timeout=50)
        try:
            dict = r.json()
            itemId = dict["files"][0]["itemId"]
            if new:
                newItemInfo.append({"recordId": recordId, "itemId": itemId})
                newItemForThumbInfo.append({"recordId": recordId, "itemId": itemId})
        except:
            pass


    @task
    def getComments(self):
        recordId = getRecordId()
        userId = getAccessUserId()
        self.client.get(url= "/api/client/records/" + str(recordId) + "/comments",
                        headers= genHeaders(userId), name="/records/[recordId]/comments", timeout=50)

    @task
    def postComment(self):
        userId = getAccessUserId()
        recordId = getRecordId()
        payload={"value":"確認しました。よろしくお願いいたします。"}
        self.client.post(url="/api/client/records/" + str(recordId) + "/comments",
                        headers= genHeaders(userId),
                        json=payload, name="/records/[recordId]/comments", timeout=50)

    @task
    def updateRecord(self):
        userId = getAccessUserId()
        recordId = getRecordId()
        status = "closed"
        payload={"status":status}
        self.client.put(url="/api/client/records/" + str(recordId),
                        headers= genHeaders(userId),
                        json=payload, name="/records/[recordId]", timeout=50)

    @task
    def postRecord(self):
        userId = getAccessUserId()
        categoryId = random.randint(1, 10)
        file = getNewFileInfo()
        payload={"title":"シナリオによる申請です。","detail": genDetail(), "categoryId": str(categoryId), \
        "fileIdList":[file]}
        r = self.client.post(url="/api/client/records",
                        headers= genHeaders(userId),
                        json=payload, name="/records", timeout=50)
        try:
            dict = r.json()
            newRecordId.append(dict["recordId"])
        except:
            pass


    @task
    def postFile(self):
        userId = getAccessUserId()
        payload=fileJson
        r = self.client.post(url="/api/client/files",
                        headers= genHeaders(userId),
                        json=payload, name="/files", timeout=50)
        try:
            dict = r.json()
            newFileId.append(dict)
        except:
            pass
    @task
    def getCategories(self):
        recordId = getRecordId()
        userId = getAccessUserId()
        self.client.get(url= "/api/client/categories/",
                        headers= genHeaders(userId), name="/categories", timeout=50)

    @task
    def tomeActive(self):
        userId = getAccessUserId()
        self.client.get(url="/api/client/record-views/tomeActive",
                        headers= genHeaders(userId), name="/record-views/tomeActive", timeout=50)
    @task
    def allActive(self):
        userId = getAccessUserId()
        self.client.get(url="/api/client/record-views/allActive",
                        headers= genHeaders(userId), name="/record-views/allActive", timeout=50)
    @task
    def allClosed(self):
        userId = getAccessUserId()
        self.client.get(url="/api/client/record-views/allClosed",
                        headers= genHeaders(userId), name="/record-views/allClosed", timeout=50)
    @task
    def mineActive(self):
        userId = getAccessUserId()
        self.client.get(url="/api/client/record-views/mineActive",
                        headers= genHeaders(userId), name="/record-views/mineActive", timeout=50)

    @task
    def getFileItem(self):
        userId = getAccessUserId()
        recordId = getRecordId()
        itemId = recordId * 2
        tlock = threading.Lock()
        with tlock:
            try:
                if len(newItemInfo) != 0:
                    info = newItemInfo.pop()
                    recordId = info["recordId"]
                    itemId = info["itemId"]
            except:
                pass
        self.client.get(url="/api/client/records/" + str(recordId) + "/files/" + str(itemId),
                        headers= genHeaders(userId), name="/records/[recordId]/files/[itemId]", timeout=50)

    @task
    def getFileItemThumb(self):
        userId = getAccessUserId()
        recordId = getRecordId()
        itemId = recordId * 2
        tlock = threading.Lock()
        with tlock:
            try:
                if len(newItemForThumbInfo) != 0:
                    info = newItemForThumbInfo.pop()
                    recordId = info["recordId"]
                    itemId = info["itemId"]
            except:
                pass
        self.client.get(url="/api/client/records/" + str(recordId) + "/files/" + str(itemId) + "/thumbnail",
                        headers= genHeaders(userId), name="/records/[recordId]/files/[itemId]/thumbnail", timeout=50)
