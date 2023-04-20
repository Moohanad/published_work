import numpy as np
import pandas as pd
import math
import os

dir_name='../moduleVles/'
format='.csv'

def studVle(mn,mp):
    vle=pd.read_csv(r'../oulad_data/vle.csv')
    cols=['code_module','code_presentation','id_student','id_site','date','sum_click']
    #df=pd.read_csv('oulad_data/studentVle_D3_13B.csv',usecols=cols)
    n=mn[0]+mp[2:]
    p=os.path.join(dir_name, n + format)
    mbeh=pd.read_csv(p,usecols=cols)
    mbeh=mbeh[mbeh['date']>=0]
    mvle=vle.loc[(vle['code_module']==mn) & (vle['code_presentation']==mp)].copy()
    mvle.drop(['week_from','week_to','code_module','code_presentation'],axis=1,inplace=True)
    
    mclicks = mbeh.merge(mvle,on='id_site')
    students_clicks = pd.pivot_table(mclicks, index=['id_student'], 
    columns='activity_type',values='sum_click', aggfunc='sum', fill_value=0).apply(pd.to_numeric,downcast='integer')#.astype(np.int16)
    
    return students_clicks
    
def StuAssessemnts(mn,mp):
    assessments=pd.read_csv('../oulad_data/assessments.csv')
    studentAssessment = pd.read_csv('../oulad_data/studentAssessment.csv')
    
    ma=assessments.loc[(assessments['code_module']==mn) & (assessments['code_presentation']==mp)]
    #assessments_ids=assessments.loc[(assessments['code_module']==mn) & (assessments['code_presentation']==mp)].sort_values(by=['date'], ascending=True).id_assessment
    assessments_ids=ma[ma['weight']!=0].sort_values(by=['date'], ascending=True).id_assessment
    sa=studentAssessment[studentAssessment['id_assessment'].isin(assessments_ids)]
    mAssessments=sa.merge(ma,on='id_assessment')
    #mAssessments['w']=mAssessments.apply(lambda row: math.floor(row.date/7 -1 )+1,axis=1)
    #mAssessments['g']=mAssessments.apply(lambda row: (row.score*row.weight)/100,axis=1)

    mAssessments['g']=mAssessments.apply(lambda row: round((row.score*row.weight)/100,2),axis=1)
    mAssessments_red=mAssessments[['id_student','assessment_type','g']]
    agg_assessments = pd.pivot_table(mAssessments_red, index=['id_student'], 
    columns='assessment_type',values='g', aggfunc='sum', fill_value=0).apply(pd.to_numeric,downcast='float')
    
    return agg_assessments
    
def comb_info(vles_ass,studInfo):
        return vles_ass.merge(studInfo, left_index=True, right_index=True, how='left')
    
def combine_vles_ass(vles,ass,hk='outer'):#ass refres to assessmnets by weeks dictionary
    vcols=vles.columns.tolist()
    asscols=ass.columns.tolist()
    tmp=vles.merge(ass, left_index=True, right_index=True, how=hk).fillna(0)
    tmp[vcols]=tmp[vcols].apply(pd.to_numeric,downcast='integer')
    tmp[asscols]=tmp[asscols].apply(pd.to_numeric,downcast='float')
    #tmp.fillna(tmp.dtypes.replace({'float32': 0.0,'int16':0,'O': 'NULL'}), downcast='infer', inplace=True)


    return tmp

def stuInfo(mn,mp,spec_cols=[],only_result=False):
    sinfo= pd.read_csv(r'../oulad_data/studentInfo.csv')
    msi=sinfo.loc[(sinfo['code_module']==mn) & (sinfo['code_presentation']==mp)].set_index('id_student')
    del sinfo
    final_result_dic={"Withdrawn":1,"Fail":1,"Pass":0, "Distinction":0}
    msi['final_result'].replace(final_result_dic,inplace=True)
    if only_result:
        return msi['final_result']
        
    stu_cols=['gender','region','highest_education','imd_band','age_band','num_of_prev_attempts','studied_credits','disability','final_result']
    ##stu_info=msi[stu_cols].copy()
    ##imd_band_mapping={'0-10%':1,'10-20':2,'20-30%':3,'30-40%':4,'40-50%':5,'50-60%':6,'60-70%':7,'70-80%':8,'80-90%':9,'90-100%':10}
    ##he_mapping={'A Level or Equivalent':3,'Lower Than A Level':2,'HE Qualification':4,'Post Graduate Qualification':5,'No Formal quals':1}
    ##age_mapping={'0-35':1,'35-55':2,'55<=':3}
    #stu_info['imd_band']=stu_info['imd_band'].map(imd_band_mapping)
    #stu_info['highest_education']=stu_info['highest_education'].map(he_mapping)
    #stu_info['age_band']=stu_info['age_band'].map(age_mapping)
    ##stu_info['imd_band'].replace(imd_band_mapping,inplace=True)
    ##stu_info['highest_education'].replace(he_mapping,inplace=True)
    ##stu_info['age_band'].replace(age_mapping,inplace=True)
    '''if not spec_cols:
        spec_cols.append('final_result')
        return stu_info[spec_cols]'''
    return msi[stu_cols]