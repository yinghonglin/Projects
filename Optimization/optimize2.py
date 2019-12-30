# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#import libraries
import pandas as pd
from gurobipy import GRB, Model

def optimize(inputFile,outputFile):
    """
    this function will take inputFile and run a series of optimization, whose result will be expored to outputFile.
    """
    
    # Load data
    Flavor_Prod=pd.read_excel(inputFile,sheet_name='Flavor_Prod')
    S=pd.read_excel(inputFile,sheet_name='S',index_col=0)
    S2=pd.read_excel(inputFile,sheet_name='S2',index_col=0)
    D=pd.read_excel(inputFile,sheet_name='D',index_col=0)
    D2=pd.read_excel(inputFile,sheet_name='D2',index_col=0)
    T=pd.read_excel(inputFile,sheet_name='T',index_col=0)

    #get a list of Cat_Flavor
    Cat_Flavor=Flavor_Prod.Cat_Flavor.unique()

    #get a set of product, source warehouse, and destination warehouse for each Cat_Flavor f
    Prod={}
    Sou={}
    Des={}

    #this allow user to access a list of product, source warehouse, and destination warehouse for a particular Cat_Flavor f
    for i in range(len(Cat_Flavor)):
        Prod[Cat_Flavor[i]]=Flavor_Prod[Flavor_Prod['Cat_Flavor']==Cat_Flavor[i]]['BDC_x']
        Sou[Cat_Flavor[i]]=S[S['Cat_Flavor']==Cat_Flavor[i]]["source_warehouse"]
        Des[Cat_Flavor[i]]=D[D['Cat_Flavor']==Cat_Flavor[i]]["destination_warehouse"]

    #declare data
    mod=Model()
    I=T.index
    J=T.columns
    K=Flavor_Prod['BDC_x']
    F=Flavor_Prod['Cat_Flavor']

    #add variables
    x=mod.addVars(I,J,K,name='x')
    y=mod.addVars(I,J,name='y')
    z=mod.addVars(I,J,K,vtype=GRB.BINARY,name='z')

    #set objective
    mod.setObjective(sum(y[i,j]*T.loc[i,j] for i in I for j in J))

    #add constraint for auxilary variable y to be equal to sum of x_k
    for i in I:
        for j in J:
            mod.addConstr(y[i,j]==sum(x[i,j,k] for k in K))

    for f in F:
        #check if a certain source warehouse, destination warehouse, product is within the declared variable
        SouL=Sou[f][Sou[f].isin(I)]
        DesL=Des[f][Des[f].isin(J)]
        ProdL=Prod[f][Prod[f].isin(K)]

        #to avoid index error, only add constraint when all list is not empty
        #because in smaller sample input that only contains partial data
        #Sou[f], Des[f], and Prod[f] might not contain anything, which will give index error message
        if min(len(SouL),len(DesL),len(ProdL))>0:
            for i in SouL:
                mod.addConstr(sum(x[i,j,k] for j in J for k in ProdL)<=S2.loc[f,i])
            for j in DesL: 
                mod.addConstr(sum(x[i,j,k] for i in I for k in ProdL)>=D2.loc[f,i])

            #add lower bound to product quantity for each flavor, each source warehouse and destination warehouse
            #add a large number to enable x to have positive value when Z is 1
            for i in SouL:
                for j in DesL:
                    for k in ProdL:
                        mod.addConstr(x[i,j,k]>=500*z[i,j,k])
                        mod.addConstr(x[i,j,k]<=10000000*z[i,j,k])

            #add constraint to enforce each flavor from each route has at least two two item        
            mod.addConstr(sum(z[i,j,k] for i in SouL for j in DesL for k in ProdL)>=2)

    mod.optimize()

    #create a list to record x value if it exists
    itemlist=[]
    for f in F:
        for i in I:
            for j in J:
                for k in K:
                    if x[i,j,k].x:
                        itemlist.append([f,i,j,k,x[i,j,k].x]) 

    #convert itemlist to a dataframe
    itemlist=pd.DataFrame(itemlist,columns=["flavor","source_warehouse","destination_warehouse",
                                           "BDC","quantity"])

    #merge itemlist with Flavor_Prod to get Cat_Flavor
    final = itemlist.merge(Flavor_Prod, how='left', left_on='BDC',right_on='BDC_x')\
            [['source_warehouse','destination_warehouse','BDC','quantity','Cat_Flavor']]

    #store optimal value to a dataframe
    val=pd.DataFrame([mod.objVal],columns=['Objective Value'])

    #output data and write sheets
    writer = pd.ExcelWriter(outputFile)
    val.to_excel(writer, sheet_name='Summary',index=False)
    final.to_excel(writer, sheet_name='Solution',index=False)
    writer.save()

if __name__=='__main__':
    import sys
    print (f'Running {sys.argv[0]} using argument list {sys.argv}')

