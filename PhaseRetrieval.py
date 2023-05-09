import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import cvxpy as cp
import pdb
import random
import os
from fractions import Fraction

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

#Spider-DRO algorithm
def Spider_PhaseRetrieval(A,y_true,total_iters,epoch_vt,epoch_momentum,gamma,S0,S1,beta=0,z0=None,\
                          normalize_power=1.0,grad_max=0.0,epoch_eval=1,print_progress=False):        
    m,d=A.shape
    grad_max*=grad_max
    A_H=np.conjugate(A.T)
    if z0 is None:
        z0=np.random.normal(scale=np.sqrt(0.5),size=d)#+1j*np.random.normal(scale=np.sqrt(0.5),size=d)
    
    z_err_set=[]
    obj_set=[]
    grad_norm_set=[]
    iters_set=[]
    complexity_set=[]
    complexity=0
    zt=z0.copy()
    z_old=mt=Az_old=y_old=v_old=None
    for k in range(total_iters):
        if print_progress:
            print(str(k)+"-th iteration")
        Az=A.dot(zt)
        y=np.absolute(Az)**2
        
        if k%epoch_eval==0:
            if print_progress:
                print("evaluating "+str(k)+"-th iteration")
            z_err_set+=[np.sqrt(np.sum(np.absolute(zt-z_true)**2))]
            obj_set+=[((y_true-y)**2).mean()/2]
            grad=A_H.dot(Az*(y-y_true))/m
            grad_norm_set+=[np.sqrt(np.sum(np.absolute(grad)**2))]
            iters_set+=[k]
            complexity_set+=[complexity]
            
        if k%epoch_vt==0:
            complexity+=S0
            batch=np.random.choice(m, S0, replace=False)
            vt=A_H[:,batch].dot(Az[batch]*(y[batch]-y_true[batch]))/S0
        else:
            complexity+=S1
            batch=np.random.choice(m, S1, replace=False)
            gt=A_H[:,batch].dot(Az[batch]*(y[batch]-y_true[batch]))/S1
            g_old=A_H[:,batch].dot(Az_old[batch]*(y_old[batch]-y_true[batch]))/S1
            vt=v_old+gt-g_old
        
        if (beta==0) | (k%epoch_momentum==0):
            m_next=vt.copy()
        else:
            m_next=beta*mt+(1-beta)*vt
        
        z_old=zt.copy()
        Az_old=Az.copy()
        v_old=vt.copy()
        y_old=y.copy()
        mt=m_next.copy()
        if normalize_power==0:
            zt=zt-gamma*m_next
        else:
            norm_sq=max(np.sum(np.absolute(m_next)**2),grad_max)
            # norm_sq=max(norm_sq,0.0001)
            coeff=gamma/(norm_sq**(normalize_power/2))
            zt=zt-coeff*m_next

    return zt,z_err_set,obj_set,grad_norm_set,iters_set,complexity_set

def num2str_neat(num):
    a=Fraction(num)
    if abs(a.numerator)>100:
        a=Fraction(num).limit_denominator()
        return(str(a.numerator)+'/'+str(a.denominator))
    return str(num)
    
# S0=n_train
# S1=int(np.floor(np.sqrt(S0)))

#hyperparameters
num_exprs=1   #number of experiments
m=3000  #number of samples
d=100    #dimensionality
y_std=4.0  #noise std of y

total_iters_GDs=500
total_iters_stoc=500

# epoch_momentum=1
# beta=0
epoch_eval=1

print_progress=False
percentile=95
colors=['red','black','blue','green','cyan','purple','gold','lime','darkorange']
markers=['.','v','s','P','*']
label_size=16
num_size=14
lgd_size=18
bottom_loc=0.1
left_loc=0.15

#Add hyperparameters for obtaining final results
folder="./Phase_results"
if not os.path.isdir(folder):
    os.makedirs(folder)
S1=50
hyps=[{'epoch_vt':1,'gamma':8e-4,'S0':m,'S1':None,'normalize_power':0,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':'GD'}]
hyps+=[{'epoch_vt':1,'gamma':0.03,'S0':m,'S1':None,'normalize_power':1/3,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':r'$\frac{1}{3}$'+'GD'}]
hyps+=[{'epoch_vt':1,'gamma':0.1,'S0':m,'S1':None,'normalize_power':2/3,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':r'$\frac{2}{3}$'+'GD'}]
hyps+=[{'epoch_vt':1,'gamma':0.2,'S0':m,'S1':None,'normalize_power':1,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':'1-GD'}]
hyps+=[{'epoch_vt':1,'gamma':0.9,'S0':m,'S1':None,'normalize_power':1,'grad_max':100.0,'beta':0,'epoch_momentum':1,'legend':'Clipped GD'}]
hyps+=[{'epoch_vt':1,'gamma':2e-4,'S0':S1,'S1':None,'normalize_power':0,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':'SGD'}]
hyps+=[{'epoch_vt':1,'gamma':2e-3,'S0':S1,'S1':None,'normalize_power':1,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':'Normalized SGD'}]
hyps+=[{'epoch_vt':1,'gamma':3e-3,'S0':S1,'S1':None,'normalize_power':1,'grad_max':0,'beta':1e-4,'epoch_momentum':total_iters_stoc+9,'legend':'Normalized SGDm'}]
hyps+=[{'epoch_vt':1,'gamma':0.3,'S0':S1,'S1':None,'normalize_power':1,'grad_max':1000.0,'beta':0,'epoch_momentum':1,'legend':'Clipped SGD'}]
hyps+=[{'epoch_vt':5,'gamma':0.01,'S0':m,'S1':S1,'normalize_power':1,'grad_max':0,'beta':0,'epoch_momentum':1,'legend':'SPIDER'}]
# for normalize_power in normalize_power_Spider:
#     hyps+=[{'epoch_vt':100,'gamma':0.01,'S0':m,'S1':50,'normalize_power':normalize_power,'beta':0,\
#             'epoch_momentum':1,'legend':num2str_neat(normalize_power)+'-Spider'}]

results={}
for hyp in hyps:
    results[str(hyp)]={}
        

# random.seed(1)
np.random.seed(1)
z_true=np.random.normal(scale=np.sqrt(0.5),size=d)#+1j*np.random.normal(scale=np.sqrt(0.5),size=d)
# z_true=z_true/np.sqrt(np.sum(np.absolute(z_true)**2))
A=np.random.normal(scale=np.sqrt(0.5),size=(m,d))#+1j*np.random.normal(scale=np.sqrt(0.5),size=(m,d))   #m*d matrix whose r-th column is a_r*
# A+=(0.04/m)*np.array(range(m)).reshape((m,1))
# A=A/np.sqrt(np.sum(np.absolute(A)**2,axis=1).reshape((-1,1)))
Az_true=A.dot(z_true)
y_true=np.absolute(Az_true)**2+np.random.normal(scale=y_std,size=m)

#Initialize
z0=np.random.normal(scale=np.sqrt(0.5),size=d)#+1j*np.random.normal(scale=np.sqrt(0.5),size=d)
z0+=5
A_H=np.conjugate(A.T)

hyp=hyps[2].copy()
z1,z_err_set,obj_set,grad_norm_set,iters_set,complexity_set=Spider_PhaseRetrieval\
    (A,y_true,total_iters=100,epoch_vt=hyp['epoch_vt'],epoch_momentum=hyp['epoch_momentum'],\
     gamma=hyp['gamma'],S0=m,S1=None,beta=hyp['beta'],z0=z0,normalize_power=hyp['normalize_power'],\
        grad_max=hyp['grad_max'],epoch_eval=1,print_progress=False)

for kk in range(num_exprs):  
    for hyp_str in results.keys():
        hyp=eval(hyp_str)
        epoch_vt=hyp['epoch_vt']
        gamma=hyp['gamma']
        S0=hyp['S0']
        S1=hyp['S1']
        normalize_power=hyp['normalize_power']
        beta=hyp['beta']
        epoch_momentum=hyp['epoch_momentum']
        grad_max=hyp['grad_max']
        method=hyp['legend']
        print("Begin "+str(kk)+"-th experiment, final result: method="+str(method)+", normalize_power="+str(normalize_power))
        z0alg=z0.copy()  
        if ("SGD" in hyp['legend']) or ("SPIDER" in hyp['legend']):
            z0alg=z1.copy()        
            
        is_stoc=("SGD" in hyp['legend']) or ("SPIDER" in hyp['legend'])
        if is_stoc:
            T=total_iters_stoc
        else:
            T=total_iters_GDs
        
        zt,z_err_set,obj_set,grad_norm_set,iters_set,complexity_set=Spider_PhaseRetrieval\
            (A,y_true,T,epoch_vt,epoch_momentum,gamma,S0,S1,beta,z0alg,\
             normalize_power,grad_max,epoch_eval,print_progress)

        if kk==0:
            len1=len(z_err_set)
            results[hyp_str]['z_err']=np.zeros((num_exprs,len1))
            results[hyp_str]['obj']=np.zeros((num_exprs,len1))
            results[hyp_str]['grad_norm']=np.zeros((num_exprs,len1))
            results[hyp_str]['iters']=iters_set
            results[hyp_str]['complexity']=complexity_set
            
        results[hyp_str]['z_err'][kk,:]=z_err_set
        results[hyp_str]['obj'][kk,:]=obj_set
        results[hyp_str]['grad_norm'][kk,:]=grad_norm_set
    
xlabels={'iters':'Iteration t','complexity':'Sample Complexity'}
ylabels={'z_err':r'$||z_t-z^*||$','obj':r'$f(z_t)$','grad_norm':r'$||\nabla f(z_t)||$'}


x_max=np.inf    
for hyp in hyps:
    x_max=min(x_max,results[str(hyp)]['complexity'][-1])
    
for y_type in ['obj']:
    for x_type in ['complexity','iters']:
        if x_type=="complexity":
            opt_type="stoc"
        else:
            opt_type="GD"
        plt.figure(figsize=(6,6))
        k=0
        for hyp_str in results.keys():
            hyp=eval(hyp_str)
            is_stoc=("SGD" in hyp['legend']) or ("SPIDER" in hyp['legend'])
            if opt_type=="GD" and is_stoc:
                continue
            if opt_type=="stoc" and (not is_stoc):
                continue
            if not np.any(results[hyp_str][y_type]>2*results[hyp_str][y_type].reshape(-1)[0]):
                beta=hyp['beta']
                x_plot=np.array(results[hyp_str][x_type])
                if x_type=='complexity':
                    indexes=(x_plot<=x_max)
                    upper_loss = np.percentile(results[hyp_str][y_type], percentile, axis=0)
                    lower_loss = np.percentile(results[hyp_str][y_type], 100 - percentile, axis=0)
                    avg_loss = np.mean(results[hyp_str][y_type], axis=0)
                    plt.plot(x_plot[indexes],avg_loss[indexes],color=colors[k],marker=markers[k],markevery=int(len(avg_loss[indexes])/(k+6)),label=hyp['legend'])
                    if num_exprs>1:
                        plt.fill_between(x_plot[indexes],lower_loss[indexes],upper_loss[indexes],color=colors[k],alpha=0.3,edgecolor="none")
                else:
                    upper_loss = np.percentile(results[hyp_str][y_type], percentile, axis=0)
                    lower_loss = np.percentile(results[hyp_str][y_type], 100 - percentile, axis=0)
                    avg_loss = np.mean(results[hyp_str][y_type], axis=0)
                    plt.plot(x_plot,avg_loss,color=colors[k],marker=markers[k],markevery=int(len(avg_loss)/(k+6)),label=hyp['legend'])
                    if num_exprs>1:
                        plt.fill_between(x_plot,lower_loss,upper_loss,color=colors[k],alpha=0.3,edgecolor="none")
                k+=1
        plt.rc('axes', labelsize=label_size)   # fontsize of the x and y labels
        plt.rc('xtick', labelsize=num_size)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=num_size)    # fontsize of the tick labels
        plt.legend(prop={'size':lgd_size},loc=1)
        plt.xlabel(xlabels[x_type])
        plt.ylabel(ylabels[y_type])
        plt.gcf().subplots_adjust(bottom=bottom_loc)
        plt.gcf().subplots_adjust(left=left_loc)
        plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
        if opt_type=="GD":
            plt.yscale("log")
        plt.savefig(folder+'/'+y_type+'VS'+x_type+'_'+opt_type+'_FinalResults.png',dpi=200)
        plt.close()
            
hyp_txt=open(folder+'/hyperparameters.txt','w')
k=0
for hyp in hyps:
    hyp_txt.write('Hyperparameter '+str(k)+':\n')
    k+=1
    for hyp_name in list(hyp.keys()):
        hyp_txt.write(hyp_name+':'+str(hyp[hyp_name])+'\n')
    hyp_txt.write('\n\n')
hyp_txt.close()

