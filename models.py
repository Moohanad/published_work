import matplotlib.pyplot as plt
#from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
#from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_validate
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
from sklearn.preprocessing import StandardScaler

def apply_models(weekdf):#def apply_models(Xtr,ytr,Xte,yte):
    Xtr=weekdf.copy()
    ytr=Xtr.pop('final_result')
    scale_features_std = StandardScaler()
    X = scale_features_std.fit_transform(Xtr)

    models=[]
    models.append(('NB', GaussianNB()))
    models.append(('RF',RandomForestClassifier()))
    models.append(('LR',LogisticRegression(max_iter=250)))
    accdic={}
    f1dic={}
    scoring = ['accuracy','f1']

    for name, model in models:
        dic2={}
        kfold = StratifiedKFold(n_splits=10)
        if name=='LR':
        
            scores=cross_validate(model, X, ytr, cv=kfold, scoring=scoring)#changed Xtr to X for lr issue
        else :
            scores=cross_validate(model, Xtr, ytr, cv=kfold, scoring=scoring)#changed Xtr to X for lr issue
        #dic2['acc']=scores['test_'+'accuracy'].mean()
        #dic2['f1']=scores['test_'+'f1'].mean()
        #dic1[name]=dic2
        accdic[name]=scores['test_'+'accuracy'].mean().round(3)
        f1dic[name]=scores['test_'+'f1'].mean().round(3)

    return (accdic,f1dic)