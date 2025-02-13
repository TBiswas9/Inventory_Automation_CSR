# pyinstaller --onefile -w Filename.py
# pip install pyinstaller

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import *
import pandas as pd
from datetime import datetime
import os

class InventoryGUI:
    def __init__(self,parent):
        self.parent = parent
        self.parent.title("PHMG CSR inventory")
        self.parent.geometry('700x250')
        self.parent.configure(bg="light blue")
        self.parent.resizable(False,False)
        self.label_message = tk.Label(self.parent,text = "Load Raw files for the inventory creation",bg="light blue")
        self.label_message.grid(column=0, row=0)

        self.frame1=tk.Frame(self.parent,borderwidth=5,width=700, height=50, background="light blue")
        self.frame1.grid(column=0, row=1)
        self.entry_file1 = tk.Entry(self.frame1,width=80)
        self.entry_file1.grid(column=0, row=1)

        self.frame4=tk.Frame(self.parent,borderwidth=5,width=60, height=50,background="light blue")
        self.frame4.grid(column=2, row=1)
        self.button_browse1 = tk.Button(self.frame4, text="Aging.csv",command=self.browse1 ,relief="raise", padx=5,pady=5,width=20,bg="light green")
        self.button_browse1.grid(column=2, row=1)

        self.frame2=tk.Frame(self.parent,borderwidth=3,width=700, height=50, bg="light blue")
        self.frame2.grid(column=0, row=3)
        self.entry_file2 = tk.Entry(self.frame2,width=80)
        self.entry_file2.grid(column=0, row=3)

        self.frame5=tk.Frame(self.parent,borderwidth=5,width=60, height=50,background="light blue")
        self.frame5.grid(column=2, row=3)
        self.button_browse2 = tk.Button(self.frame5, text="Gurantor.csv",command=self.browse2 ,relief="raise", padx=5,pady=5,width=20,bg="light green")
        self.button_browse2.grid(column=2, row=3)       

        self.frame3=tk.Frame(self.parent,borderwidth=5,width=380, height=50,background="light blue")
        self.frame3.grid(column=0, row=7)
        self.button_run = tk.Button(self.frame3, text="Create Inventory",command=self.file ,relief='raise', padx=5, pady=5, width=30, bg="light green")
        self.button_run.grid(column=0, row=7)

        self.frame6=tk.Frame(self.parent,borderwidth=5,width=380, height=50,background="light blue")
        self.frame6.grid(column=2, row=7)
        self.button_close = tk.Button(self.frame6, text="Close",command=self.terminate_app, relief='raise', padx=5, pady=5, width=20, bg="orange")
        self.button_close.grid(column=2, row=7)

    def browse1(self):
        path = fd.askopenfilename(title='Aging.csv')
        if path:
            self.entry_file1.delete(0, tk.END)
            self.entry_file1.insert(0, path)

    def browse2(self):
        path = fd.askopenfilename(title='Gurantor.csv')
        if path:
            self.entry_file2.delete(0, tk.END)
            self.entry_file2.insert(0, path)

    def file(self):
        file_Name1 = self.entry_file1.get()
        file_Name2 = self.entry_file2.get()
        if file_Name1 == "":
            messagebox.showinfo("Information","Enter the file path for Aging")
        elif file_Name2 == "":
            messagebox.showinfo("Information","Enter the file path for Gurantor")
        else:
            self.run_cat(file_Name1, file_Name2)

    def terminate_app(self):
        self.parent.destroy()

    def run_cat(self,file_Name1, file_Name2):
        try:
            #Aging = pd.read_excel(file_Name1)#, sheet_name='Aging012425')
            Aging = pd.read_csv(file_Name1)
            Guarantor = pd.read_csv(file_Name2)
            Guarantor = Guarantor[['E/I','Prac Name','Acct Nbr']]
            Guarantor['E/I']=Guarantor['E/I'].astype(float)
            Guarantor['UID'] = Guarantor[['E/I','Prac Name']].astype(str).agg("-".join, axis=1)
            Aging['UID'] = Aging[['E/I/A/B','Prac Name']].astype(str).agg("-".join, axis=1)
            Guarantor = Guarantor.copy()
            Guarantor.drop_duplicates(inplace=True)
            Aging = Aging[['Name','Birth Dt','Pat Amt','UID','Prac Name']]
            Aging['Pat Amt'] = '$'+Aging['Pat Amt'].astype(str)
            Aging['Pat Amt'] = Aging.loc[:,'Pat Amt'].str.replace(
                '$', "", regex=False)\
                    .str.replace('(', "-", regex=False)\
                        .str.replace(')', "", regex=False)\
                            .str.replace(',', "", regex=False)\
                                .str.replace(" ","", regex=False)
            Aging['Pat Amt'] = Aging['Pat Amt'].astype(float)
            Pat_AR = Aging[Aging['Pat Amt']!=0]
            Pat_AR = Pat_AR.groupby(by=['Name','Birth Dt','UID','Prac Name'])['Pat Amt'].sum().reset_index()
            Pat_AR = Pat_AR.merge(Guarantor[['UID','Acct Nbr']], how='left', on ='UID')
            CSR = Pat_AR.groupby(by = ['Name','Birth Dt','Acct Nbr'])['Pat Amt'].sum().reset_index(name = 'Bal_Amt')
            Lookup = ('ZZZ','ZZz','ZzZ','zZZ','Zzz','zZz','zzZ','zzz','**')
            CSR=CSR[~CSR['Name'].str.startswith(Lookup)]            
            CSR[['Patient_Last_Name','Patient_First_Name']] = CSR['Name'].str.split(",",n=1,expand=True,)
            #CSR = CSR.drop(CSR[CSR['Name'].str.startswith("**")].index, axis=0)
            #CSR = CSR.drop(CSR[CSR['Name'].str.startswith("ZZZ")].index, axis=0)
            CSR.rename(columns={'Acct Nbr':'Person_Account_Number','Birth Dt':'Patient_DOB','Bal_Amt':'Balance_Amount'}, inplace=True)
            CSR['Facility code']  = 'PHMG'
            CSR = CSR[['Facility code','Patient_Last_Name','Patient_First_Name','Person_Account_Number','Patient_DOB','Balance_Amount']]
            CSR = CSR[CSR['Balance_Amount']>0]
            now = datetime.now()
            now_str = now.strftime('%m%d%Y')
            base_location = os.getcwd()
            output_path = base_location + "\\" + "PHMG_CA_" + now_str + ".csv"
            CSR.to_csv(output_path, index=False)
            messagebox.showinfo("Success", f"Report saved successfully : {output_path}")
        
        except Exception as e:
            messagebox.showerror('Error', f"Error occurred: {str(e)}")


def main():
    root = tk.Tk()
    Inventory = InventoryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
