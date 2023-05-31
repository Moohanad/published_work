import numpy as np
import pandas as pd
import math
import os

dir_name='../moduleVles/'
format='.csv'

def reg_drop(code_mod,code_present):
    reg = pd.read_csv(r'../oulad_data/studentRegistration.csv')
    regs=reg.loc[(reg['code_module']==code_mod) & (reg['code_presentation']==code_present)]
    reg_drops=regs.loc[regs['date_unregistration']<0]['id_student'].copy()
    return reg_drops
    
def studVle(mn,mp):
    vle=pd.read_csv(r'../oulad_data/vle.csv')
    cols=['code_module','code_presentation','id_student','id_site','date','sum_click']
    #df=pd.read_csv('oulad_data/studentVle_D3_13B.csv',usecols=cols)
    n=mn[0]+mp[2:]
    p=os.path.join(dir_name, n + format)
    mbeh=pd.read_csv(p,usecols=cols)
    mbeh['w']=mbeh.apply(lambda row: math.floor(row.date/7 -1 )+1,axis=1)
    mbeh.drop(['date'],axis=1,inplace=True)
    bterm=mbeh[mbeh['w']<0]
    mbeh=mbeh[mbeh['w']>=0] 
    mvle=vle.loc[(vle['code_module']==mn) & (vle['code_presentation']==mp)].copy()
    mvle.drop(['week_from','week_to','code_module','code_presentation'],axis=1,inplace=True)
    #return mvle
    bterm_clicks= bterm.merge(mvle,on='id_site')

    mclicks = mbeh.merge(mvle,on='id_site')
    student_summary_by_week = pd.pivot_table(mclicks, index=['w','id_student'], 
    columns='activity_type',values='sum_click', aggfunc='sum', fill_value=0)#.apply(pd.to_numeric,downcast='integer')#.astype(np.int16)
    bt_clicks = pd.pivot_table(bterm_clicks, index='id_student',values='sum_click', aggfunc='sum')

    idx= student_summary_by_week.index.get_level_values('w').unique()
    W=[]
    for i in idx:
        W.append(student_summary_by_week.loc[i])#.apply(pd.to_numeric,downcast='integer')
        
    weeks_dic={}
    for i in range(1,idx.max()+1):
        temp_list=[]
        for j in range(i+1):
            temp_list.append(W[j])
        weeks_dic[j]=pd.concat(temp_list).groupby('id_student').sum()#.apply(pd.to_numeric,downcast='integer')
        temp_list.clear()

    #return student_summary_by_week
    return weeks_dic,bt_clicks

def StuAssessemnts(mn,mp, comb=True):
    assessments=pd.read_csv('../oulad_data/assessments.csv')
    studentAssessment = pd.read_csv('../oulad_data/studentAssessment.csv')
    
    ma=assessments.loc[(assessments['code_module']==mn) & (assessments['code_presentation']==mp)]
    #assessments_ids=assessments.loc[(assessments['code_module']==mn) & (assessments['code_presentation']==mp)].sort_values(by=['date'], ascending=True).id_assessment
    assessments_ids=ma[ma['weight']!=0].sort_values(by=['date'], ascending=True).id_assessment
    sa=studentAssessment[studentAssessment['id_assessment'].isin(assessments_ids)]
    mAssessments=sa.merge(ma,on='id_assessment')
    mAssessments['w']=mAssessments.apply(lambda row: math.floor(row.date/7 -1 )+1,axis=1)
    mAssessments['g']=mAssessments.apply(lambda row: (row.score*row.weight)/100,axis=1)
    mAssessments_red=mAssessments[['id_student','assessment_type','w','g']]
    Assessments_red_weeks = pd.pivot_table(mAssessments_red, index=['w','id_student'], 
    columns='assessment_type',values='g', aggfunc='sum', fill_value=0)#.apply(pd.to_numeric,downcast='float')
    
    assessments_weeks={}
    #asses_w=sorted(Assessments_red_weeks['w'].unique())
    asses_w=sorted(Assessments_red_weeks.index.unique(level='w'))
    for k in asses_w:
        #assessments_weeks[k]=Assessments_red_weeks.loc[k]
        tmp=Assessments_red_weeks.loc[k]
        assessments_weeks[k]=tmp.loc[:, (tmp != 0).any(axis=0)]#.apply(pd.to_numeric,downcast='float')
        
    if comb:
        for k in asses_w:
            tmp=assessments_weeks[k]
            cols=tmp.columns
            nCol='w'+str(k)
            #tmp['nCol']=df.apply(lambda row: row.a + row.b, axis=1)
            #df['c'] = df.apply(lambda row: row.a + row.b, axis=1)
            tmp[nCol] = tmp.sum(axis=1)
            tmp.drop(cols,axis=1,inplace=True)
            assessments_weeks[k]=tmp
            del tmp
    return assessments_weeks
    
def combine_vles_ass(vles,ass):#ass refres to assessmnets by weeks dictionary
    vle_ass_dic=vles.copy()
    for k in ass.keys():
        #vle_ass_dic[k]=vle_ass_dic[k].merge(ass[k], left_index=True, right_index=True, how='outer').fillna(0)
        vle_ass_dic[k]=vle_ass_dic[k].merge(ass[k], left_index=True, right_index=True, how='outer')
        vle_ass_dic[k].fillna(vle_ass_dic[k].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)


    return vle_ass_dic

def stuInfo(mn,mp,spec_cols=[],only_result=False):
    sinfo= pd.read_csv(r'../oulad_data/studentInfo.csv')
    msi=sinfo.loc[(sinfo['code_module']==mn) & (sinfo['code_presentation']==mp)].set_index('id_student')
    del sinfo
    final_result_dic={"Withdrawn":1,"Fail":1,"Pass":0, "Distinction":0}
    msi['final_result'].replace(final_result_dic,inplace=True)
    if only_result:
        return msi['final_result']
        
    stu_cols=['gender','region','highest_education','imd_band','age_band','num_of_prev_attempts','studied_credits','disability','final_result']
    stu_info=msi[stu_cols].copy()
    imd_band_mapping={'0-10%':1,'10-20':2,'20-30%':3,'30-40%':4,'40-50%':5,'50-60%':6,'60-70%':7,'70-80%':8,'80-90%':9,'90-100%':10}
    he_mapping={'A Level or Equivalent':3,'Lower Than A Level':2,'HE Qualification':4,'Post Graduate Qualification':5,'No Formal quals':1}
    age_mapping={'0-35':1,'35-55':2,'55<=':3}
    #stu_info['imd_band']=stu_info['imd_band'].map(imd_band_mapping)
    #stu_info['highest_education']=stu_info['highest_education'].map(he_mapping)
    #stu_info['age_band']=stu_info['age_band'].map(age_mapping)
    stu_info['imd_band'].replace(imd_band_mapping,inplace=True)
    stu_info['highest_education'].replace(he_mapping,inplace=True)
    stu_info['age_band'].replace(age_mapping,inplace=True)
    '''if not spec_cols:
        spec_cols.append('final_result')
        return stu_info[spec_cols]'''
    return stu_info
    
#def ret_cols(mn,mp,spec_cols):
    
    
def vle_ass_info(vle_ass_weeks,studInfo):
    vle_assessments_df={}
    for key in vle_ass_weeks.keys():
    #vle_assessments_demo_df[key]=vle_assessments_weeks[key].merge(d13b_studentInfo['final_result'], left_index=True, right_index=True, how='left')
        #vle_assessments_df[key]=vle_ass_weeks[key].merge(d13b_studentInfo['final_result'], left_index=True, right_index=True, how='left')
        vle_assessments_df[key]=vle_ass_weeks[key].merge(studInfo, left_index=True, right_index=True, how='left')
    return vle_assessments_df
        
def comb_info(weeks_dfs,studInfo):
    new_df={}
    for key in weeks_dfs.keys():
        new_df[key]=weeks_dfs[key].merge(studInfo, left_index=True, right_index=True, how='left')
    return new_df
def combine_until(ass_weeks):
    
    new_ass_weeks={}            
    lst1=list(ass_weeks.keys())
    if not new_ass_weeks:
        fk=lst1[0]
        sk=lst1[1]   
        #k=str(fk)+str(sk)
        new_ass_weeks[fk]=ass_weeks[fk].copy()#changed 5-3-22
        new_ass_weeks[sk]=pd.concat([ass_weeks[fk],ass_weeks[sk]],axis=1)#.fillna(0) if this activated no need to to the below step 
        new_ass_weeks[sk].fillna(new_ass_weeks[sk].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)

    for i in range(2,len(lst1)):
        pk=lst1[i-1]
        ck=lst1[i]
        #k=str(pk)+str(ck)
        new_ass_weeks[ck]=pd.concat([new_ass_weeks[pk],ass_weeks[ck]],axis=1)#.fillna(0)
        new_ass_weeks[ck].fillna(new_ass_weeks[ck].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)

    return new_ass_weeks
    

def dup_ass(wukeys,vkeys):#wukeys is the until week dict of dataframes 
    nkeys={}
    #for ind in range (1,wukeys[0]):
    #    nkeys[ind]=ind
    i=0
    while(i<len(wukeys)-1):
        k=wukeys[i]
        while k < wukeys[i+1]:
            nkeys[k]=wukeys[i]
            k=k+1
        i=i+1
    nkeys[k]=wukeys[i]
    return nkeys

def comVleAss(vles,untilAss):# combine until week datasets that accumulate previous assessemnts until a certain week with vle data
    duplst=dup_ass(list(untilAss.keys()),list(vles.keys()))
    fdf=vles.copy()
    for k in duplst.keys():
        fdf[k]=fdf[k].merge(untilAss[duplst[k]], left_index=True, right_index=True, how='outer')#.fillna(0)
        fdf[k].fillna(fdf[k].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)    
    return fdf

    
'''    for k in vles.keys():
        if k not in duplst.keys():
            fdf[k]=vles[k].copy()
        else:
            fdf[k]=vles[k].merge(untilAss[k], left_index=True, right_index=True, how='outer')#.fillna(0)
            fdf[k].fillna(fdf[k].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)    
    return fdf '''
# the below was not used frequently need to check later
def finalize_df(until_ass,vles):
    fdf={}

    keys=list(until_ass.keys())
    #keys2=list(vles.keys())
    for i in range(1,keys[0]):
        fdf[i]=vles[i].copy()

    i=0
    k=keys[0]    
    while(i< len(keys)-1):
        while (k < keys[i+1]):
            fdf[k]=vles[k].merge(until_ass[keys[i]], left_index=True, right_index=True, how='outer')#.fillna(0)
            fdf[k].fillna(fdf[k].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)
            k=k+1
        i=i+1
    fdf[k]=vles[k].merge(until_ass[keys[i]], left_index=True, right_index=True, how='outer')#.fillna(0)
    fdf[k].fillna(fdf[k].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)    
    return fdf
    
def change_ass_weeks_names(ass_weeks):
    lst=['CMA','TMA']
    for k in ass_weeks.keys():
        for x in lst:
            if x in ass_weeks[k].columns:
                new_name=x+str(k)
                ass_weeks[k].rename(columns={x:new_name},inplace=True)
    return ass_weeks

def combine_weeks_ass_until(ass_weeks):
    lst=['CMA','TMA']
    for k in ass_weeks.keys():
        for x in lst:
            if x in ass_weeks[k].columns:
                new_name=x+str(k)
                ass_weeks[k].rename(columns={x:new_name},inplace=True)
                
    new_ass_weeks={}            
    lst1=list(ass_weeks.keys())
    if not new_ass_weeks:
        fk=lst1[0]
        sk=lst1[1]   
        #k=str(fk)+str(sk)
        new_ass_weeks[fk]=ass_weeks[fk]
        new_ass_weeks[sk]=pd.concat([ass_weeks[fk],ass_weeks[sk]],axis=1)#.fillna(0)
        new_ass_weeks[sk].fillna(new_ass_weeks[sk].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)

   
    for i in range(2,len(lst1)):
        pk=lst1[i-1]
        ck=lst1[i]
        #k=str(pk)+str(ck)
        new_ass_weeks[ck]=pd.concat([new_ass_weeks[pk],ass_weeks[ck]],axis=1)#.fillna(0)
        new_ass_weeks[ck].fillna(new_ass_weeks[ck].dtypes.replace({'float64': 0.0,'int64':0, 'O': 'NULL'}), downcast='infer', inplace=True)
    return new_ass_weeks

