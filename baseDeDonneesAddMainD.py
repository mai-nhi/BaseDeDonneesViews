import mariadb
import json
import re
import pandas as pd
import numpy
import requests

url = 'https://gaia.fantasiapp.tech:2810'
tokenRqst = '{"entreprise":"front.back","type":"login","username":"mainhi","isCloud":true,"proposedPwd":"pwd"}'
rqTok = requests.post(url, data = tokenRqst)
Tokk = json.loads(rqTok.text)["token"]
rqst = {}
rqst["id"] = 6
rqst["entreprise"] = "front.back"
rqst["token"] = Tokk
rqst["type"] = "getData"
rqst["username"] = "mainhi"
rqst["proposedPwd"] = "pwd"
rqst["isCloud"] = True
rqst["isExpert"] = False
rqst["relation"] = "hdwork"
rqst["fields"] = ["id","name","hdworkInfo","categ_id","laborId","articleInfo"]
rqst["conditions"] = []
rqst["query"] = "metal"
rqst["joins"] = [{
    "joinTable":"labor",
    "joinField":"laborId",
    "targetIdField":"BIMid",
    "targetFields":["BIMid","name","categ_id","laborInfo"]}]
data = json.dumps(rqst)
x = requests.post(url, data = data)
hdwork = json.loads(x.text)["data"]



fileTab = pd.read_excel("./tabPanelBlock.xlsx")


connection=mariadb.connect(
        user="mainhi",
        password="1234",
        host="localhost",
        database="testOuvrage",
        autocommit=True)
cursor = connection.cursor()


cursor.execute("SELECT BIMid,fatherId FROM hdwork_category WHERE id >= 135;")
categoryUnder = cursor.fetchall()

cursor.execute("SELECT BIMid,fatherId FROM hdwork_category WHERE (id < 135 AND id >= 11);")
categoryFamilly = cursor.fetchall()

cursor.execute("SELECT BIMid,fatherId FROM hdwork_category WHERE (id < 11 AND id >= 1);")
categoryGroup = cursor.fetchall()

#cursor.execute("SELECT BIMid,hdworkInfo,articleInfo,categ_id FROM hdwork;")
#hdwork = cursor.fetchall()


lstCategoryFamilly = []
lstCategoryGroup = []
lstCategoryUnder = []
lstBim = [['',None]]

lstFalse = []

for tup in categoryUnder:
    lstCategoryUnder+=[[tup[0],None, tup[1]]]
for tup in categoryFamilly:
    lstCategoryFamilly+=[[tup[0], None, tup[1]]]
for tup in categoryGroup:
    lstCategoryGroup+=[[tup[0], None, tup[1]]]
lstHdwork = []





#for tup in hdwork:
#    saveJson = {**json.loads(tup[1]) , **json.loads(tup[2])}
#    lstHdwork+=[[tup[0],saveJson, tup[3]]]











for value in hdwork:
    lstHdwork+=[[value["BIMid"],value, value["categ_id"]]]
    del(value["BIMid"])
    del(value["categ_id"])
for value in lstHdwork:
    #print(value[1])
    if value[2] == None:
        lstFalse += [value[0]]
    else:
        categId = int(value[2]) - 135
        if lstCategoryUnder[categId][1] == None:
            lstCategoryUnder[categId][1] = []
            for libelle, val in value[1].items():
                lstCategoryUnder[categId][1] += [libelle]
        else:
            save = []
            for libelle in lstCategoryUnder[categId][1]:
                if libelle in value[1]:
                    save += [libelle]
            lstCategoryUnder[categId][1] = save

def delNoneValueInDict(lst : list):
    save = []
    for value in lst:
        if value[1] != None:
            save += [value]
    return save

def newNode(lstEnd :list, lstStart :list, offSet : int):
    for index, value in enumerate(lstStart):
        if value[1] == None:
            continue
        fatherId = int(value[2]) - offSet
        if lstEnd[fatherId][1] == None:
            lstEnd[fatherId][1] = []
            for val in value[1]:
                lstEnd[fatherId][1] += [val]
        else:
            saveEnd = []
            for libelle in lstEnd[fatherId][1]:
                if libelle in value[1]:
                    saveEnd += [libelle]
            lstEnd[fatherId][1] = saveEnd
    return lstEnd, lstStart

def delInStart(lstEnd : list, lstStart : list, offset : int):
    for index,value in enumerate(lstStart):
        if value[1] == None:
            continue
        fatherId = int(value[2]) - offset
        save = []
        for libelle in value[1]:
            #print("fatherId  "+str(fatherId))
            #print(len(lstEnd))
            #print("lstEnd "+ str(lstEnd[fatherId]))
            if libelle not in lstEnd[fatherId][1]:
                save += [libelle]
        lstStart[index][1] = save
    return lstStart

#lstCategoryUnder = delNoneValueInDict(lstCategoryUnder)
lstCategoryFamilly, lstCategoryUnder = newNode(lstCategoryFamilly, lstCategoryUnder, 11)
#lstCategoryFamilly = delNoneValueInDict(lstCategoryFamilly)
lstCategoryUnder = delInStart(lstCategoryFamilly, lstCategoryUnder,11)
lstCategoryGroup, lstCategoryFamilly = newNode(lstCategoryGroup, lstCategoryFamilly,1)
#lstCategoryGroup = delNoneValueInDict(lstCategoryGroup)
lstCategoryFamilly = delInStart(lstCategoryGroup, lstCategoryFamilly,1)
lstBim, lstCategoryGroup = newNode(lstBim, lstCategoryGroup,0)
lstCategoryGroup = delInStart(lstBim, lstCategoryGroup,0)
#lstBim = delNoneValueInDict(lstBim)

fileLstNoneUnder = open("lstNoneUnder", "w")
fileLstNoneUnder.write(str(lstFalse))
fileLstNoneUnder.close()

fieldsBim = {"bim":{
    "title":"Ouvrages",
    "belongsTo":"biblio",
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
            "fields":[{
                "dbField":"BIMid",
                "label":"Réf. Ouvrage",
                "type":"string",
                "width" : "1"},
                {
                "dbField":"name",
                "label":"Libellé",
                "type":"string",
                "width" : "1"}]},
        "industry":
            {"label": 'Siniat', 
            "image":'Icons/Siniat.png', 
            "icons":[
#                {"label":'Fiche système', 
#                "icon": "Icons/Page-1.png", 
#                "link":'Fiche système' },
#                {"label":'Vidéo de mise en œuvre', 
#                "icon": 'Icons/video.png', 
#                "link":'Vidéo de mise en œuvre' },
#                {"label":'URL Justificatif reaction au feu', 
#                "icon": 'Icons/Page-1.png', 
#                "link":'URL Justificatif reaction au feu' },
#                {"label":'URL Justificatif acoustique', 
#                "icon": 'Icons/music.house.png', 
#                "link":'URL Justificatif acoustique' },
#                {"label":'URL notice de montage', 
#                "icon": 'Icons/list.bullet.be', 
#                "link":'URL notice de montage' }
                ]}
        }},

    "tabs":[{
        "id":"0",
        "title":"hdwork"},
        {"id":"1",
        "title":"Déboursé"},
        {"id":"2",
        "title":"Fournitures"},
        {"id":"3",
        "title":"Main d'oeuvre"},
        {"id":"4",
        "title":"Autres dépenses"},
        {"id":"5",
        "shadow" : "true",
        "icon" : "Icons/description.png",
        "title":"Description"},
        {"id":"6",
        "shadow" : "true",
        "icon" : "Icons/product.png",
        "title":"BIM"}],

    "panels":[{
        "id":"7",
        "parentPath":["1", "7"],
        "title":"",
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
        "title":"décomposition des taches(hors joints)",
        "hide":True,},
        {"id":"13",
        "parentPath":["4","13"],
        "title":"main d'oeuvre interne",
        "hide":True},
        {"id":"14",
        "parentPath":["4","14"],
        "title":"sous-traitance",
        "hide":True},
        {"id":"15",
        "parentPath":["6", "15"],
        "title":"",
        "hide":True,},
        {"id":"17",
        "parentPath":["5", "17"],
        "title":"descriptif commercial",
        "hide":True,},
        {"id":"16",
        "parentPath":["0", "16"],
        "title":"",
        "hide":True},
        {"id":"18",
        "parentPath":["5", "18"],
        "title":"descriptif technique",
        "hide":True}],

    "blocks":[{"id": "28",
        "parentPath": ["0", "16", "28"],
        "title":"hdworkPB",
        "type":"standard"},
        {"id": "16",
        "parentPath": ["1","7","16"],
        "title":"",
        "type":"composition-graph"},
        {"id":"17",
        "parentPath" : ["2","8","17"],
        "title": 'Matières premières', 
        "type": 'grouping-table', 
        "expandable": "true",  
        "colDefs":[
            {"headerName": "Référence", "field": "position"},
            {"headerName": "Libellé article", "field": "name"},
            {"headerName": "rank", "field": "rank", "regroup": "true", "hide": "true"},
            {"headerName": "Ratio au M2", "field": "ratio"},
            {"headerName": "U.P.", "field": "up"},
            {"headerName": "P.U.", "field": "pu"},
            {"headerName": "Total", "field": "total"}]},
        {"id": "18",
        "parentPath": ["2","8","18"],
        "title":"Matiériel et outillage",
        "type":"standard"},
        {"id": "19",
        "parentPath": ["3","9","19"],
        "title":"",
        "type":"pie-chart"},
        {"id": "20",
        "parentPath": ["3","10","20"],
        "title":"Coûts horaires/M.O interne",
        "type":"standard"},
        {"id": "21",
        "parentPath": ["3","10","21"],
        "title" : "Budget ouvrage//M.O interne",
        "type":"standard"},
        {"id": "22",
        "parentPath": ["3","10","22"],
        "title":"Temps de pose & prix unitaires//M.O interne",
        "type":"standard"},
        {"id": "23",
        "parentPath": ["3","11","23"],
        "title":"Budget ouvrage/sous-traitant",
        "type":"standard"},
        {"id": "24",
        "parentPath": ["3","11","24"],
        "title":"Décomposition des prix unitaires/sous-traitant",
        "type":"standard"},
        {"id": "25",
        "parentPath": ["4","12","25"],
        "title":"",
        "type":"standard"},
        {"id": "33",
        "parentPath": ["4","13","33"],
        "title":"coûts horaires / M.O. interne",
        "type":"standard"},
        {"id": "34",
        "parentPath": ["4","13","34"],
        "title":"budget ouvrage / M.O. interne",
        "type":"standard"},
        {"id": "35",
        "parentPath": ["4","13","35"],
        "title":"temps de pose & prix unitaires / M.O. interne",
        "type":"standard"},
        {"id": "36",
        "parentPath": ["4","14","36"],
        "title":"budget ouvrage / sous-traitant",
        "type":"standard"},
        {"id": "37",
        "parentPath": ["4","14","37"],
        "title":"decomposition des prix unitaires / sous-traitant",
        "type":"standard"},
        {"id": "26",
        "parentPath": ["6","15","26"],
        "title":"",
        "type":"standard"},
        {"id": "27",
        "parentPath" : ["5","17","27"],
        "title" : "descriptifs et benefices",
        "type" : "standard"},
        {"id" : "29",
        "parentPath" : ["5", "18", "29"],
        "title" : "performances mécaniques",
        "type" : "standard"},
        {"id": "30",
        "parentPath": ["5", "18", "30"],
        "title":"résistance au feu",
        "type":"standard"},
        {"id": "31",
        "parentPath": ["5", "18", "31"],
        "title":"performances acoustiques",
        "type":"standard"},
        {"id": "32",
        "parentPath": ["5", "18", "32"],
        "title":"autres informations",
        "type":"standard"},
        {"id":"33",
        "parentPath" : ["3","10","21","33"],
        "title":"circle graph",
        "type":"circles-graph",
        "fields":[{"dbField" : "budg_appr","label" : "Budget appro. & pose","type" : 'string'},
        {"dbField" : "budg_jnts","label" : "Budget joints","type" : "string"},
        {"dbField" : "budg_autr","label" : "Budget autres Travaux","type" : "string"}]},
        {"id":"34",
        "parentPath" : ["3","10","20","34"],
        "title": 'Pie-Chart', 
        "type": 'circles-graph',
        "fields" :[{"dbField" : "hor_brp_ch","label" : "Taux horaire brut poseur(s) non chargé","type" : 'string'},
        {"dbField" : "hor_brp_nch","label" : "Taux horaire brut poseur(s) chargé","type" : 'string'},
        {"dbField" : "hor_br_ch","label" : "Taux horaire brut chargé","type" : 'string'},
        {"dbField" : "hor_br_nch","label" : "Taux horaire brut non chargé","type" : 'string'}]}],
    "fields":[]
    }

def addCellFieldsJson(lst : list):
    for index, value in enumerate(lst):
        lstFields = value[1]
        familly = value[0]
        newCell = {
            "tabs":None,
            "panels":None,
            "blocks":None,
            "fields":[]
        }
        if value[1] == None:
            continue
        for field in lstFields:
            if field.strip() not in fileTab:
                fileTab[field.strip()] = None
            idFields = fileTab.loc[7, field.strip()]
            if type(fileTab.loc[0, field.strip()]) != numpy.float64 :
                tabId = fileTab.loc[0, field.strip()]
            else :
                tabId = "0"
            if type(fileTab.loc[1, field.strip()]) != numpy.float64:
                panelId = fileTab.loc[1, field.strip()]
            else :
                panelId = "16"
            if type(fileTab.loc[2, field.strip()]) != numpy.float64 :
                blockId = fileTab.loc[2, field.strip()]
            else :
                blockId = "28"
            if type(fileTab.loc[3, field.strip()]) != numpy.float64:
                width = fileTab.loc[3, field.strip()]
            else :
                width = "1"
            if type(fileTab.loc[4, field.strip()]) != numpy.float64 :
                dbField = fileTab.loc[4, field.strip()]
            else :
                dbField = field
            if type(fileTab.loc[5, field.strip()]) != numpy.float64 :
                label = fileTab.loc[5, field.strip()]
            else:
                label = field
#            if type(fileTab.loc[9,field.strip()]) != numpy.float64 :
#                rank = None
#            else:
#                rank = fileTab.loc[9,field.strip()]    
            if tabId == 2:
                newCell["fields"] += [{
                    "id":str(idFields),
                    "dbField":"",
                    "position":dbField,
                    "name":dbField,
                    "rank": str(fileTab.loc[9, field.strip()]),
                    "parentPath":[str(tabId),str(panelId),str(blockId),str(idFields)],
                    "ratio":None,
                    "up":None,
                    "total":None,
                    "pu" : None
                }]
            else:    
                newCell["fields"] += [{
                    "id":str(idFields),
                    "dbField":dbField,
                    "label":label,
                    "type":"textarea",
                    "parentPath":[str(tabId),str(panelId),str(blockId),str(idFields)],
                    "width":str(width)
                }]


        #print(type(newCell))
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


for field in lstBim[0][1]:
    if field.strip() not in fileTab:
        fileTab[field.strip()] = None
    idFields = fileTab.loc[7, field.strip()]
    if type(fileTab.loc[0, field.strip()]) != numpy.float64:
        tabId = fileTab.loc[0, field.strip()]
    else :
        tabId = "0"
    if type(fileTab.loc[1, field.strip()]) != numpy.float64:
        panelId = fileTab.loc[1, field.strip()]
    else :
        panelId = "16"
    if type(fileTab.loc[2, field.strip()]) != numpy.float64:
        blockId = fileTab.loc[2, field.strip()]
    else :
        blockId = "28"
    if type(fileTab.loc[3, field.strip()]) != numpy.float64:
        width = fileTab.loc[3, field.strip()]
    else :
        width = "1"
    if type(fileTab.loc[4, field.strip()]) != numpy.float64 :
        dbField = fileTab.loc[4, field.strip()]
    else :
        dbField = field
    if type(fileTab.loc[5, field.strip()]) != numpy.float64 :
        label = fileTab.loc[5, field.strip()]
    else:
        label = field
#    print(type(fileTab.loc[9,field.strip()]))
#    if type(fileTab.loc[9,field.strip()]) == float :
#        rank = None
#    else:
#        rank = fileTab.loc[9,field.strip()]    
#    print(tabId)
    if fileTab.loc[0, field.strip()] == "Basic":
        fieldsBim["bim"]["form"]["basicInfo"]["fields"] += [{
                "dbField": dbField,
                "label": label,
                "type":"string",
                "width" : str(width)
        }]
    elif tabId == 2:
        fieldsBim["fields"] += [{
            "id":str(idFields),
            "dbField":"",
            "position":dbField,
            "name":dbField,
            "rank": str(fileTab.loc[9, field.strip()]),
            "parentPath":[str(tabId),str(panelId),str(blockId),str(idFields)],
            "ratio":None,
            "up":None,
            "total":None,
            "pu":None
        }]        
    elif fileTab.loc[0, field.strip()] == "Industry":
        fieldsBim["bim"]["form"]["industry"]["icons"] += [{
                "label":dbField, 
                "icon": fileTab.loc[6, field.strip()], 
                "link":dbField,
                "iconId":str(fileTab.loc[8, field.strip()])
        }]
    else: 
        fieldsBim["fields"] += [{
            "id":str(idFields),
            "dbField":dbField,
            "label":label,
            "type":"textarea",
            "parentPath":[str(tabId),str(panelId),str(blockId),str(idFields)],
            "width" : str(width)
        }]







path = r"./tabV2.xlsx"

writer = pd.ExcelWriter(path, engine = "xlsxwriter")
fileTab.to_excel(writer, sheet_name = "tab")
writer.save()






















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
