import mariadb
import json
import re
import pandas as pd
import numpy

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
            if type(fileTab.loc[0, field.strip()]) != numpy.float64 :
                tabId = fileTab.loc[0, field.strip()]
            else :
                tabId = "hdwork"
            if type(fileTab.loc[1, field.strip()]) != numpy.float64:
                panelId = fileTab.loc[1, field.strip()]
            else :
                panelId = "hdworkP"
            if type(fileTab.loc[2, field.strip()]) != numpy.float64 :
                blockId = fileTab.loc[2, field.strip()]
            else :
                blockId = "hdworkPB"
            newCell["fields"] += [{
                "dbField":"description",
                "label":field,
                "type":"textarea",
                "tabId":str(tabId),
                "panelId":str(panelId),
                "blockId":str(blockId)
            }]
        print(type(newCell))
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

fieldsBim = {"bim":{
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
        }}},

    "tabs":[{
        "id":"1",
        "title":"Déboursé"},
        {"id":"2",
        "title":"Fournitures"},
        {"id":"3",
        "title":"Main d'oeuvre"},
        {"id":"4",
        "title":"Autres dépenses"},
        {"id":"5",
        "title":"Description"},
        {"id":"6",
        "title":"BIM"},
        {"id":"hdwork",
        "title":"hdwork"}],

    "panels":[{
        "id":"7",
        "parentPath":["1", "7"],
        "title":"Vide1",
        "hide":True,},
        {"id":"8",
        "parentPath":["2", "8"],
        "title":"Déboursés fourniture",
        "hide":True,},
        {"id":"9",
        "parentPath":["3", "9"],
        "title":"Décomposition des tâches (hors joints)",
        "hide":True,},
        {"id":"10",
        "parentPath":["3", "10"],
        "title":"Main d'oeuvre interne",
        "hide":True,},
        {"id":"11",
        "parentPath":["3", "11"],
        "title":"Sous-traitance",
        "hide":True,},
        {"id":"12",
        "parentPath":["4", "12"],
        "title":"Vide2",
        "hide":True,},
        {"id":"13",
        "parentPath":["5", "13"],
        "title":"Vide3",
        "hide":True,},
        {"id":"14",
        "parentPath":["6", "14"],
        "title":"Vide4",
        "hide":True,},
        {"id":"hdworkP",
        "parentPath":None,
        "title":"",
        "hide":True}],
    
    "blocks":[{"id": "15",
        "parentPath": ["1","7","15"],
        "title":"Vide5",
        "type":"standard"},
        {"id": "16",
        "parentPath": ["2","8","16"],
        "title":"Matières premières",
        "type":"standard"},
        {"id": "17",
        "parentPath": ["2","8","17"],
        "title":"Matiériel et outillage",
        "type":"standard"},
        {"id": "18",
        "parentPath": ["3","9","18"],
        "title":"Vide6",
        "type":"standard"},
        {"id": "19",
        "parentPath": ["3","10","19"],
        "title":"Coûts horaires/M.O interne",
        "type":"standard"},
        {"id": "20",
        "parentPath": ["3","10","20"],
        "title":"Budget ouvrage//M.O interne",
        "type":"standard"},
        {"id": "21",
        "parentPath": ["3","10","21"],
        "title":"Temps de pose & prix unitaires//M.O interne",
        "type":"standard"},
        {"id": "22",
        "parentPath": ["3","11","22"],
        "title":"Budget ouvrage/sous-traitant",
        "type":"standard"},
        {"id": "23",
        "parentPath": ["3","11","23"],
        "title":"Décomposition des prix unitaires/sous-traitant",
        "type":"standard"},
        {"id": "24",
        "parentPath": ["4","12","24"],
        "title":"Vide7",
        "type":"standard"},
        {"id": "25",
        "parentPath": ["5","13","25"],
        "title":"Vide8",
        "type":"standard"},
        {"id": "26",
        "parentPath": ["6","14","26"],
        "title":"Vide9",
        "type":"standard"},
        {"id": "hdworkPB",
        "parentPath": None,
        "title":"",
        "type":"standard"}],
    "fields":[]
    }


for field in lstBim[""]:
    if type(fileTab.loc[0, field.strip()]) != numpy.float64:
        tabId = fileTab.loc[0, field.strip()]
    else :
        tabId = "hdwork"
    if type(fileTab.loc[1, field.strip()]) != numpy.float64:
        panelId = fileTab.loc[1, field.strip()]
    else :
        panelId = "hdworkP"
    if type(fileTab.loc[2, field.strip()]) != numpy.float64:
        blockId = fileTab.loc[2, field.strip()]
    else :
        blockId = "hdworkPB"
    fieldsBim["fields"] += [{
        "dbField":"description",
        "label":field,
        "type":"textarea",
        "tabId":str(tabId),
        "panelId":str(panelId),
        "blockId":str(blockId)
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
