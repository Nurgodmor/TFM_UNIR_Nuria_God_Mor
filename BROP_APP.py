import sys
import sqlite3
from sqlite3 import Error
from PyQt5.QtCore import QSize
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import os
import datetime
from PyQt5 import uic
from PyQt5 import QtSql
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt5.uic.uiparser import QtCore
from PyQt5.QtGui import QIcon
from BROP import Ui_BROP

class GUI (QMainWindow,Ui_BROP) : 

    def __init__(self) :
        QMainWindow.__init__(self)
        Ui_BROP.__init__(self)
        self.setupUi(self)
        # Botones
        self.Boton_P_Trait.clicked.connect(self.browsefile_ptrait)
        self.Boton_RSeg.clicked.connect(self.browsefile_Rseg)
        self.Boton_RComercial.clicked.connect(self.browsefiles_RComercial)
        # BBDD
        self.btn_consultar_datos.clicked.connect(self.consultar_datos)
        self.Descargar.clicked.connect(self.descargar)
        self.mensajes = QMessageBox()
        self.mensajes.setWindowFilePath('Mensajes')
        #self.txt_nombre_bbdd.addItem("2021")
        #self.txt_nombre_bbdd.addItem("2022")
        #self.txt_nombre_bbdd.addItem("2023")
        self.tbl_datos.setAlternatingRowColors(True)
        self.show()

    def consultar_datos(self):
        self.tbl_datos.clear()
        name_db = self.txt_nombre_bbdd.text().strip()
        name_db = name_db + '.db'
        if os.path.exists(name_db):
            name_table = self.txt_nombre_tabla.text().strip()
            conn = sqlite3.connect(name_db)
            cur = conn.cursor()
            listOfTables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = :tabla", {"tabla":name_table}).fetchall()

            if listOfTables == []:
                self.mensajes.setText('El archivo seleccionado no esta disponible')
                self.mensajes.setIcon(QMessageBox.Warning)
                self.mensajes.exec_()
    
            else:
                #read_df=pd.read_sql('SELECT * FROM ' + name_table,conn)
                try:
                    query = 'SELECT * FROM {}'.format(name_table)
                    result = cur.execute(query)
                    names = list(map(lambda x: x[0], result.description))
                    self.tbl_datos.setHorizontalHeaderLabels(names)

                    for row_number, row_data in enumerate ( result ):
                        self.tbl_datos.insertRow ( row_number )

                        for colum_number, data in enumerate ( row_data ):
                            self.tbl_datos.setItem ( row_number, colum_number, QTableWidgetItem ( str ( data ) ) )
                except Error as e:
                    self.mensajes.setText('Se ha producido un error a la hora de conectar con la base de datos')
                    self.mensajes.setIcon(QMessageBox.Warning)
                    self.mensajes.exec_()
                finally:
                    conn.close()
        else:
            self.mensajes.setText('El año seleccionado no esta disponible')
            self.mensajes.setIcon(QMessageBox.Warning)
            self.mensajes.exec_()
    

    def descargar(self):
        name_db = self.txt_nombre_bbdd.text().strip()
        name_db = name_db + '.db'
        if os.path.exists(name_db):
            name_table = self.txt_nombre_tabla.text().strip()
            conn = sqlite3.connect(name_db)
            cur = conn.cursor()
            listOfTables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = :tabla", {"tabla":name_table}).fetchall()

            if listOfTables == []:
                self.mensajes.setText('El archivo seleccionado no esta disponible')
                self.mensajes.setIcon(QMessageBox.Warning)
                self.mensajes.exec_()
            else:
                read_df=pd.read_sql('SELECT * FROM ' + name_table,conn)
                read_df.to_excel(name_table +'_descarga.xlsx', index= False)

        else:
            self.mensajes.setText('El año seleccionado no esta disponible')
            self.mensajes.setIcon(QMessageBox.Warning)
            self.mensajes.exec_()


    def browsefile_ptrait(self):
        fname=QFileDialog.getOpenFileName(self, "Open File","/Documents","*.xlsx")
        path = fname[0]
        self.pTrait_calculation(path)
    
    def browsefile_Rseg(self):
        fname=QFileDialog.getOpenFileName(self, "Open File","/Documents","(*.xls;*.xlsx;*.xlsm),*.xls;*.xlsx;*.xlsm")
        path = fname[0]
        self.Rseg_calculation(path)
    
    def browsefiles_RComercial(self):
        fname=QFileDialog.getOpenFileName(self, "Open File","/Documents","(*.xls;*.xlsx;*.xlsm),*.xls;*.xlsx;*.xlsm")
        path = fname[0]
        self.Rcomer_calculation(path)

                                                             ## R_COMERCIAL ##   
    def Rcomer_calculation(self, path) :

        comercial = pd.read_excel(path,sheet_name=0, dtype=str)
        Tabla = pd.read_excel(path,sheet_name=1, dtype=str)
        comercial = comercial[comercial.columns.drop(list(comercial.filter(regex='Unnamed')))]
        Tabla = Tabla[Tabla.columns.drop(list(Tabla.filter(regex='Unnamed')))]

        path_comercial = 'comercial.csv'

        columns = list(comercial.columns )
        columns = columns[1:]
        comercial_csv = pd.read_csv(path_comercial,sep=';',engine='python',index_col = 'Condition')
        comercial_csv = comercial_csv.replace(np.nan, '', regex=True)
        comercial = comercial.replace(np.nan, '', regex=True)    


        dict = comercial_csv.to_dict()
        for i in range(len(columns)):
            for j in range(len(comercial.index)):
                if comercial[columns[i]][j] != '':
                    comercial[columns[i]][j]= dict[columns[i]][comercial[columns[i]][j]]

        r_comercial = comercial.reindex(columns=['NSTUY_pon','HR','VA_Rt-2','MI1T5_S-8','VuFF','MI5T5_S-9','LLLT_Tz-SS','XZW_PU','E3U2_Po-8','RTOE_Dm4c','RRPS_Ps3','MWDP','SEP_8.5_PII_RO4','IR','TXK_8.5_PRC_So5'])
        r_comercial['HR'] = 'HR'
        r_comercial['IR'] = 'IR'

        columns1 = list(r_comercial.columns)
        r_comercial['R_comercial'] = r_comercial[columns1].agg(';'.join, axis=1)
        r_comercial['R_comercial'] = r_comercial['R_comercial'].replace(r'[;]{2,}',';',regex=True)
        r_comercial['R_comercial'] = r_comercial['R_comercial'].replace(r'^[;]{1,}','',regex=True)
        r_comercial['R_comercial'] 

         #Guardar archivos
        fname=QFileDialog.getSaveFileName(self, "Save File",'R_comercial.xlsx',"Microsoft Excel Workbooks (*.xls;*.xlsx;*.xlsm),*.xls;*.xlsx;*.xlsm")
        save_path = fname[0]

        table_name = re.findall(r"^.*[\\/](.+?)\.[^.]+$",save_path)
        now = datetime.datetime.now()
        dbname = str(now.year)
        conn = sqlite3.connect(dbname + '.db')

        r_comercial.to_sql(table_name[0],conn,if_exists='replace')

        with pd.ExcelWriter(save_path) as writer:  
            r_comercial.to_excel(writer, sheet_name='resistencia_hibrido',index=False)

                                                                                                                     
                                                            ## FIN R_COMERCIAL ## 

                                                            ## R_SEGREGANDO ##
    def Rseg_calculation(self, path) :
        M_p_trait = pd.read_excel(path,sheet_name=0, dtype=str)
        F_p_trait = pd.read_excel(path,sheet_name=1,  dtype=str)
        sowing = pd.read_excel(path,usecols=['Plot', 'ASRT1', 'Gen', 'Pedigree', 'Origin', 'Inv BID'],sheet_name=2,  dtype=str)
        cross = pd.read_excel(path,usecols=['F', 'X', 'M', 'CROSS','Cruce padre','M_F', 'X', 'M_M'],sheet_name=3,  dtype=str)
        p_trait = pd.read_excel(path,sheet_name=4,  dtype=str)

        p_trait = p_trait[p_trait.columns.drop(list(p_trait.filter(regex='Unnamed')))]
        M_p_trait = M_p_trait[M_p_trait.columns.drop(list(M_p_trait.filter(regex='Unnamed')))]
        F_p_trait = F_p_trait[F_p_trait.columns.drop(list(F_p_trait.filter(regex='Unnamed')))]
        
        #hacemos un df para female

        female = pd.merge(cross,p_trait, left_on=['F'],right_on=['Plot'],suffixes=('_cross', '_ptrait'),how='left')
        len_madres = len(female.index)
        female = female.replace(np.nan, '', regex=True)

        Ptrait1 = p_trait[['Plot', 'P-Trait']]
        cross_new = female [['CROSS', 'F', 'X', 'M', 'Cruce padre', 'M_F', 'M_M']]

        #dataframe de la madre del padre
        cross_mf = pd.merge(cross_new,F_p_trait, left_on=['M_F'],right_on=['Plot'],how='left')
        cross_mf = cross_mf.replace(np.nan, '', regex=True)

        #dataframe del padre del padre
        cross_mm = pd.merge(cross_new,M_p_trait, left_on=['M_M'],right_on=['Plot'],how='left')
        cross_mm = cross_mm.replace(np.nan, '', regex=True)

        columns1 = list(cross_mm.columns)
        columns = columns1[14:]
 
        resistencia_hibrido = cross_mf.copy()

        for i in range(len(columns)):
            condiciones = [cross_mf[columns[i]] == cross_mm[columns[i]],
                        cross_mf[columns[i]] != cross_mm[columns[i]]]
            opciones = [cross_mf[columns[i]],'H']
            resistencia_hibrido[columns[i]] = np.select(condiciones, opciones)

        resistencia_hibrido = resistencia_hibrido.replace(np.nan, '', regex=True)

        columns_female = list(female.columns)
        new_list = list(set(columns).difference(columns_female))

        for i in range(len(new_list)):
            female[new_list[i]] = ''

        columns1 = list(resistencia_hibrido.columns)
        columns = columns1[14:]
        
        resistencia_segregando = resistencia_hibrido.copy()

        for i in range(len(columns)):
            condiciones = [resistencia_hibrido[columns[i]] == female[columns[i]],
                    resistencia_hibrido[columns[i]] != female[columns[i]]]
            opciones = [resistencia_hibrido[columns[i]],'H']
            resistencia_segregando[columns[i]] = np.select(condiciones, opciones)

        resistencia_segregando = resistencia_segregando.replace(np.nan, '', regex=True)

        dictionary= {}
        for i in range(len(columns)):
            valor= len(resistencia_segregando[resistencia_segregando[columns[i]] == 'H'])
            dictionary[columns[i]] = valor
        
        sort_orders = dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True))

        key_iterable = sort_orders.keys()
        key_list = list(key_iterable)
        cols = columns1[0:14] + key_list
        resistencia_segregando = resistencia_segregando[cols]
        resistencia_segregando

        columns1 = list(resistencia_segregando.columns)
        columns = columns1[14:]

        for i in range(len(columns)):
            condiciones = [resistencia_segregando[columns[i]] != 'H', resistencia_segregando[columns[i]] == 'H']
            opciones = ['',columns[i]]
            resistencia_segregando[columns[i]] = np.select(condiciones, opciones)

        resistencia_segregando['segregando'] = resistencia_segregando[columns].agg(';'.join, axis=1)
        resistencia_segregando['segregando']  = resistencia_segregando['segregando'].replace(r'[;]{2,}',';',regex=True)
        resistencia_segregando['segregando']  = resistencia_segregando['segregando'].replace(r'^[;]{1,}','',regex=True)
        resistencia_segregando['segregando'] 

        #Guardar archivos
        fname=QFileDialog.getSaveFileName(self, "Save File",'R_seg.xlsx',"Microsoft Excel Workbooks (*.xls;*.xlsx;*.xlsm),*.xls;*.xlsx;*.xlsm")
        save_path = fname[0]

        table_name = re.findall(r"^.*[\\/](.+?)\.[^.]+$",save_path)
        now = datetime.datetime.now()
        dbname = str(now.year)
        conn = sqlite3.connect(dbname + '.db')

        resistencia_segregando.to_sql(table_name[0],conn,if_exists='replace')

        with pd.ExcelWriter(save_path) as writer:  
            resistencia_hibrido.to_excel(writer, sheet_name='resistencia_hibrido',index=False)    
            sowing.to_excel(writer, sheet_name='sowing',index=False)
            resistencia_segregando.to_excel(writer, sheet_name='resistencia_segregando',index=False)


                                                            ## FIN R_SEGREGANDO ##

                                                                    ## P-TRAIT ##

    def pTrait_calculation(self, path) :
        sowing = pd.read_excel(path,usecols=['Plot', 'ASRT1', 'Gen', 'Pedigree', 'Origin', 'Inv BID'],sheet_name=0)
        cross = pd.read_excel(path,usecols=['F', 'X', 'M', 'CROSS', 'GOAL', 'Gen', 'FINAL_GOAL'],sheet_name=1)
        p_trait = pd.read_excel(path,sheet_name=2)

        p_trait = p_trait[p_trait.columns.drop(list(p_trait.filter(regex='Unnamed')))]

        cross_p = pd.merge(cross,p_trait, left_on=['F'],right_on=['Plot'],suffixes=('_cross', '_ptrait'),how='left')
        cross_p['F']=cross_p['F'].astype('Int64')
        cross_p['Plot']=cross_p['Plot'].astype('Int64')
        cross_p['M']=cross_p['M'].astype('Int64')
        len_madres = len(cross_p.index)
        cross_p = cross_p.replace(np.nan, '', regex=True)

        cross_p = pd.merge(cross_p,p_trait, left_on=['M'],right_on=['Plot'],suffixes=('_f', '_m'),how='left')
        cross_p['F']=cross_p['F'].astype('Int64')
        cross_p['Plot_f']=cross_p['Plot_f'].astype('Int64')
        cross_p['Plot_m']=cross_p['Plot_m'].astype('Int64')
        cross_p['M']=cross_p['M'].astype('Int64')
        len_padres = len(cross_p.index)

        cross_p = cross_p.drop(columns=['Gen','Gen_ptrait'])
        cross_p = cross_p.rename(columns={'Gen_cross':'Gen'})

        #Gráfica
        graph = cross_p[['E3U2_Po-8_f','MI5T5_S-9_f','RRPS_Ps3_f','RTOE_Dm4c_f','ZXRP_Ue-2_f','SEP_8.5_PII_RO4_f','SEP_8.5_PII_RO5_f','CA_Al-1_f', 'TXK_8.5_PRC_So5_f','CFYU_Ka-Ka_f', 'XZW_PU_f']]
        columnas = graph.columns
        pintar = pd.DataFrame(columns=["resistencia","R","S","H"])

        for i in range(len(columnas)):
            pintar.at[i,'resistencia'] = columnas[i]
            pintar.at[i,'R']= len(graph[graph[columnas[i]]== 'R'])
            pintar.at[i,'S']= len(graph[graph[columnas[i]]== 'S'])
            pintar.at[i,'H']= len(graph[graph[columnas[i]]== 'H'])
            
        pintar.plot(x="resistencia", y=["R", "H", "S"], kind="bar",figsize=(9,8))
        plt.show()

        columns = list(cross_p.columns )
        columns = columns[12:]
        columns.remove("Plot_m") 
        columns.remove("P-Trait_m") 
        columns

        f = re.compile(".*_f")
        columns_f = list(filter(f.match, columns)) # Read Note below
        print(columns_f)

        m = re.compile(".*_m")
        columns_m = list(filter(m.match, columns)) # Read Note below
        columns_m = columns_m[3:]
        print(columns_m)

        path_breeder = 'Breeder_code.csv'

        breeder_code = pd.read_csv(path_breeder,sep='[;,:\s+]',engine='python',index_col = 'Condition')
        breeder_code = breeder_code.replace(np.nan, '', regex=True)

        breeder_code_f = breeder_code
        breeder_code_f.columns = [str(col) + '_f' for col in breeder_code.columns]

        dict_f = breeder_code_f.to_dict()

        for i in range(len(columns_f)):
            for j in range(len(cross_p.index)):
                if cross_p[columns_f[i]][j] != '':
                   cross_p[columns_f[i]][j]= dict_f[columns_f[i]][cross_p[columns_f[i]][j]]

        cross_p = cross_p.replace(np.nan, '', regex=True)
        breeder_code_m = breeder_code_f
        breeder_code_m.columns = breeder_code_m.columns.str.replace("_f", "_m")
        dict_m = breeder_code_m.to_dict()

        for i in range(len(columns_m)):
            for j in range(len(cross_p.index)):
                if cross_p[columns_m[i]][j] != '':
                   cross_p[columns_m[i]][j]= dict_f[columns_m[i]][cross_p[columns_m[i]][j]]

        cross_p = cross_p.replace(np.nan, '', regex=True)
        cross_p = cross_p.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        variable = cross_p['NSTUY_pon_f']
        variable = cross_p['NSTUY_pon_f']
        cross_p.drop(labels=['NSTUY_pon_f'], axis=1,inplace = True)
        columns2 = list(cross_p.columns)
        cross_p.insert(len(columns2), 'NSTUY_pon_f', variable)

        columns2 = list(cross_p.columns)
        columns2 = columns2[12:-1]
        
        f = re.compile(".*_f")
        columns_f = list(filter(f.match, columns2))
        cross_p['P_trait_female'] = cross_p[columns_f].agg(''.join, axis=1)
        cross_p['P_trait_female'] = cross_p['P_trait_female'] + ";" + cross_p["NSTUY_pon_f"]

        cross_p['DOBLE'] = cross_p["P-Trait_m"].str.contains('/', regex=True)
        cross_p['P_trait_cross'] = ""

        cross_p.loc[cross_p['DOBLE'] == True, 'P_trait_cross'] = cross_p["P_trait_female"] + "//" + cross_p["P-Trait_m"]
        cross_p.loc[cross_p['DOBLE'] == False, 'P_trait_cross'] = cross_p["P_trait_female"] + "/" + cross_p["P-Trait_m"]

        # new_index = ['F','X','M','CROSS','GOAL','Gen','FINAL_GOAL','F']
        # cross_p.reindex(columns=new_index)


        fname=QFileDialog.getSaveFileName(self, "Save File",'P_trait.xlsx',"Microsoft Excel Workbooks (*.xls;*.xlsx;*.xlsm),*.xls;*.xlsx;*.xlsm")
        save_path = fname[0]

        table_name = re.findall(r"^.*[\\/](.+?)\.[^.]+$",save_path)
        now = datetime.datetime.now()
        dbname = str(now.year)
        conn = sqlite3.connect(dbname + '.db')


        cross_p.to_sql(table_name[0],conn,if_exists='replace')


        cross_p.columns = cross_p.columns.str.replace("_f", "")
        cross_p.columns = cross_p.columns.str.replace("_m", "")

        with pd.ExcelWriter(save_path) as writer:  
            cross_p.to_excel(writer, sheet_name='P-trait',index=False)    
            sowing.to_excel(writer, sheet_name='sowing',index=False)
            cross.to_excel(writer, sheet_name='cross',index=False)
                                                            ## FIN P-TRAIT ##
 
if __name__ == '__main__':
    app = QApplication (sys.argv)
    GUI = GUI()
    GUI.show()
    # set app icon  
    
    app_icon = QIcon()
    app_icon.addFile('img\logo32.ico',QSize(32,32))
    app_icon.addFile('img\logo.ico',QSize(64,64))
    app.setWindowIcon(app_icon)
    sys.exit(app.exec_())