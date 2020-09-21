import mariadb
import json
import re
import pandas as pd

fileTab = pd.read_excel("./tabPanelBlock.xlsx")


connection=mariadb.connect(
        user="catherine",
        password="1234",
        host="localhost",
        database="testOuvrage",
        autocommit=True)
cursor = connection.cursor()
cursor.execute("SELECT BIMid FROM hdwork_category WHERE id >= 135;")
categoryUnder = cursor.fetchall()     # resultOfQuery = cursor.fetchall()

cursor.execute("SELECT BIMid,hdworkInfo,articleInfo FROM hdwork;")
hdwork = cursor.fetchall()

cursor.execute("SELECT BIMid FROM hdwork_category WHERE (id < 135 AND id >= 11);")
categoryFamilly = cursor.fetchall()

cursor.execute("SELECT BIMid FROM hdwork_category WHERE (id < 11 AND id >= 1);")
categoryGroup = cursor.fetchall()

lstCategoryFamilly = {}
lstCategoryGroup = {}
lstCategoryUnder = {}
lstBim = {('',):None}

lstFalse = []

for tup in categoryUnder:
    lstCategoryUnder[tup] = None

for tup in categoryFamilly:
    lstCategoryFamilly[tup] = None
for tup in categoryGroup:
    lstCategoryGroup[tup] = None
lstHdwork = {}
for tup in hdwork:
    saveJson = {**json.loads(tup[1]) , **json.loads(tup[2])}
    lstHdwork[tup[0]] = saveJson
i=0
for bimId, value in lstHdwork.items():
    i+=1
    find = 0
    for category,lstLibelle in lstCategoryUnder.items():
        reg = "^{}".format(category[0])
        if re.search(reg, bimId):
            find = 1
            if lstLibelle == None:
                lstCategoryUnder[category] = []
                for libelle, value in lstHdwork[bimId].items():
                    lstCategoryUnder[category] += [libelle]
            else:
                save = []
                for libelle in lstCategoryUnder[category]:
                    if libelle in lstHdwork[bimId]:
                        save += [libelle]
                lstCategoryUnder[category] = save
        if find == 1:
            break
    if find == 0:
        lstFalse += [bimId]

def delNoneValueInDict(dictionary : dict):
    save = {}
    for i, value in dictionary.items():
        if value != None:
            save[i] = dictionary[i]
    return save

def newNode(dictEnd, dictStart):
    for bimId, value in dictStart.items():
        find = 0
        for category,lstLibelle in dictEnd.items():
            reg = "^{}".format(category[0])
            if re.search(reg, bimId[0]):
                find = 1
                if lstLibelle == None:
                    dictEnd[category[0]] = []
                    for value in dictStart[bimId]:
                        dictEnd[category[0]] += [value]
                else:
                    saveEnd = []
                    saveStart = []
                    for libelle in dictEnd[category]:
                        if libelle in dictStart[bimId]:
                            saveEnd += [libelle]
                    dictEnd[category] = saveEnd

            if find == 1:
                break
    return dictEnd, dictStart

def delInStart(dictEnd, dictStart):
    for bimId, value in dictStart.items():
        find = 0
        for category,lstLibelle in dictEnd.items():
            reg = "^{}".format(category)
            if re.search(reg, bimId[0]):
                find = 1
                save = []
                for Libelle in value:
                    if Libelle not in lstLibelle:
                        save = [Libelle]
                dictStart[bimId] = save
            if find == 1:
                break
    return dictStart

lstCategoryUnder = delNoneValueInDict(lstCategoryUnder)
lstCategoryFamilly, lstCategoryUnder = newNode(lstCategoryFamilly, lstCategoryUnder)
lstCategoryFamilly = delNoneValueInDict(lstCategoryFamilly)
lstCategoryUnder = delInStart(lstCategoryFamilly, lstCategoryUnder)
lstCategoryGroup, lstCategoryFamilly = newNode(lstCategoryGroup, lstCategoryFamilly)
lstCategoryGroup = delNoneValueInDict(lstCategoryGroup)
lstCategoryFamilly = delInStart(lstCategoryGroup, lstCategoryFamilly)
lstBim, lstCategoryGroup = newNode(lstBim, lstCategoryGroup)
lstCategoryGroup = delInStart(lstBim, lstCategoryGroup)
lstBim = delNoneValueInDict(lstBim)

fileLstNoneUnder = open("lstNoneUnder", "w")
fileLstNoneUnder.write(str(lstFalse))
fileLstNoneUnder.close()

def addCellFieldsJson(dictionary : dict):
    for familly, lstFields in dictionary.items():
        newCell = {
            "tabs":None,
            "panels":None,
            "blocks":None,
            "fields":[]
        }
        for field in lstFields:
            newCell["fields"] += [{
                "dbField":"description",
                "label":field,
                "type":"textarea",
                "tabId":fileTab.loc[1, field],
                "panelId":defPanelId[2,field],
                "blockId":defBlockId[3,field]
            }]
        if len(newCell["fields"]) > 0:
            jsonUnder = json.dumps(newCell)
            if type(familly) == tuple:
                cursor.execute("UPDATE hdwork_category SET views = ? WHERE BIMid = ?;",(jsonUnder, familly[0],))
            else:
                cursor.execute("UPDATE hdwork_category SET views = ? WHERE BIMid = ?;",(jsonUnder,familly,))
        #else:
        #    if type(familly) == tuple:
        #        cursor.execute("UPDATE hdwork_category SET views = null WHERE BIMid = ?;",(familly[0],))
        #    else:
        #        cursor.execute("UPDATE hdwork_category SET views = null WHERE BIMid = ?;",(familly,))

addCellFieldsJson(lstCategoryUnder)
addCellFieldsJson(lstCategoryFamilly)
addCellFieldsJson(lstCategoryGroup)

fieldsBim = {
    "title":"Ouvrages",
    "layout":{
        "showConfiguratorPanel":True,
        "showCategoryPanel":True,
        "showFilterDetailPanel":True,
        "showShoppingCart":True
    },
    "form":{
        "basicInfo":{
            "title":"",
            "type":"standard",
            "fields":[
            {
                "dbField":"id",
                "label":"Réf. Ouvrage",
                "type":"string"
            },
            {
                "dbField":"name",
                "label":"Libellé",
                "type":"string"
            },
            {
                "dbField":"group",
                "label":"Groupe",
                "type":"enum"
            },
            {
                "dbField":"category",
                "label":"Famille",
                "type":"enum"
            },
            {
                "dbField":"subcategory",
                "label":"Sous-famille",
                "type":"enum"
            }
          ]
        }},
    "tabs":[{
        "id":"D.1",
        "title":"Description"},
        {"id":"F.1",
        "title":"Fournitures"},
        {"id":"M.1",
        "title":"Main d'oeuvre"},
        {"id":"P.1",
        "title":"Prix de vente"},
        {"id":"B.1",
        "title":"BIM"}],
    "panels":[{
        "id":"hdworkP",
        "title":"",
        "hide":True,
        "tabId":"hdwork"}],
    "blocks":[{
        "id":"hdworkPB",
        "title":"",
        "type":"standard",
        "tabId":"hdwork",
        "panelId":"hdworkP"}],
    "fields":[]
    }


for field in lstBim[""]:
    fieldsBim["form"]["fields"] += [{
        "dbField":"description",
        "label":field,
        "type":"textarea",
        "tabId":fileTab.loc[1, field],
        "panelId":defPanelId[2,field],
        "blockId":defBlockId[3,field]
        }]
jsonBim = json.dumps(fieldsBim)    
cursor.execute("UPDATE hdwork_category SET views = ? WHERE BIMid = ?;",(jsonBim, "BIM"))
                     
#print(lstFalse)
#print(lstCategoryUnder)
#print(lstCategoryFamilly)
#print(lstCategoryGroup)
#print(lstBim)
            

#print(lstCategory)
#print(lstCategory[0])
#print(hdwork)
#print(hdwork[0][0])
cursor.close()
connection.close()
